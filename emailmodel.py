import os

def save_email(email):
    # Specify the path to your email file
    # You might want to use an absolute path depending on your deployment environment
    email_file_path = os.path.join(os.path.dirname(__file__), 'emails.txt')

    try:
        # Open the file in append mode and write the email followed by a newline
        with open(email_file_path, 'a') as file:
            file.write(email + '\n')
        return True
    except Exception as e:
        print(f"Failed to save email: {e}")
        return False
