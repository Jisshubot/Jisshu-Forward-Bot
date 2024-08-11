echo "Cloning Repo...."
if [ -z $BRANCH ]
then
  echo "Cloning main branch...."
  git clone https://github.com/Jisshubot/Jisshu_forward Jisshubot/Jisshu_forward 
else
  echo "Cloning $BRANCH branch...."
  git clone https://github.com/Jisshubot/Jisshu_forward -b $BRANCH /Jisshu_forward
fi
cd Jisshubot/Jisshu_forward 
pip3 install -U -r requirements.txt
echo "Starting Bot...."
gunicorn app:app & python3 main.py
