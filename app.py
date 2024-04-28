from flask import Flask, request, jsonify, send_file, Response
import os
import threading
import pandas as pd
from bot_module import InstagramBot
import subprocess
emails=[]

def get_connected_devices():
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')
    devices = []
    for line in output_lines[1:]:
        device_info = line.split('\t')
        if len(device_info) == 2 and device_info[1] == 'device':
            devices.append(device_info[0])
    return devices

def split_dataframe_user_names(df, num_splits):
    username_list = df['username'].tolist()

    split_size = len(username_list) // num_splits
    split_lists = [username_list[i * split_size:(i + 1) * split_size] for i in range(num_splits)]
    split_lists[-1].extend(username_list[num_splits * split_size:])
    return split_lists

def split_dataframe_login_info(df):
    username_list = df['username'].tolist()
    password_list=df['password'].tolist()
    proxy_list=df['ip'].tolist()
    return username_list,password_list,proxy_list

def perform_activities(bot):
    email=bot.other_activities()
    #emails.extend(email)
app = Flask(__name__)

@app.route('/run_bot', methods=['POST','GET'])
def run_bot():
    # Receive login_info_csv, usernames.csv, proxy_enable value, output_directory, and log_file_path
    proxy_enable = int(request.form['proxy_enable'])
    output_directory = request.form['output_directory']
    log_file_path = request.form.get('log_file_path', 'bot_logs.log')  # Default to 'bot_logs.log' if not provided

    # Save files locally
    login_info_csv = request.files['login_info_csv']
    login_info_path = os.path.join(output_directory, 'login_info.csv')
    login_info_csv.save(login_info_path)

    usernames_csv = request.files['usernames_csv']
    usernames_path = os.path.join(output_directory, 'usernames.csv')
    usernames_csv.save(usernames_path)


    connected_devices = get_connected_devices()

    if not connected_devices:
        return jsonify({'message': 'No connected devices found'})

    # Split dataframes
    login_info_df = pd.read_csv(login_info_path)
    split_dataframes_user_name = split_dataframe_user_names(pd.read_csv(usernames_path), len(connected_devices))
    user_name_list, password_list, proxy_list = split_dataframe_login_info(login_info_df)

    bots = []
    for i, device in enumerate(connected_devices):
        if proxy_enable==0:
            bot = InstagramBot(device, split_dataframes_user_name[i], user_name_list[i], password_list[i], i+1,0, proxy_enable, log_file_path)
        elif proxy_enable==1:
            bot = InstagramBot(device, split_dataframes_user_name[i], user_name_list[i], password_list[i], i+1, proxy_list[i], proxy_enable, log_file_path)

        bots.append(bot)

    # Run bots
    threads = []
    for bot in bots:
        thread = threading.Thread(target=bot.other_activities)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Combine emails from all bots
    all_emails = []
    for bot in bots:
        all_emails.extend(bot.emails)

    # Save emails to CSV
    print("Emails printing")
    emails_df = pd.DataFrame({'Emails':all_emails})
    emails_csv = emails_df.to_csv(index=False)
    print(all_emails)
    
    def generate():
        with open(log_file_path, 'rb') as log_file:
            yield log_file.read()
        yield b'\n'  # Separate log file from emails CSV
        yield emails_csv.encode()


    return Response(generate(), mimetype='text/csv')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

