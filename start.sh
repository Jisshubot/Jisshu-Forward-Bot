echo "Cloning Repo...."
if [ -z $BRANCH ]
then
  echo "Cloning main branch...."
  git clone https://github.com/Jisshubot/Jisshu-forward-bot Jisshubot/fwdbot 
else
  echo "Cloning $BRANCH branch...."
  git clone https://github.com/Jisshubot/Jisshu-forward-bot -b $BRANCH /jsfwdbot
fi
cd Jisshubot/jsfwdbot 
pip3 install -U -r requirements.txt
echo "Starting Bot...."
gunicorn app:app & python3 main.py
