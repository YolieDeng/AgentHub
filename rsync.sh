rsync -avz --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' --exclude 'logs' --exclude '.git' \
    /Users/YolieDeng/Code/AgentHub/ ubuntu@119.91.226.17:/home/ubuntu/AgentHub/