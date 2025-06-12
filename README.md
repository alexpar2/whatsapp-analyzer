This tool has been designed for whatsapp chats in European Spanish (the whole codebase is also in spanish). 
Not recommended for any other language unless you want to spend a good deal of time messing with the preprocessing.

WHAT YOU NEED:
- An exported whatsapp chat in txt
- python
- a bash terminal if you don't want to execute the scripts yourself
- A browser that's not Firefox for some reason

STEPS:
1. Move to the directory where the scripts are
2. Install requirements (python3 -m pip install -r requirements.txt)
3. Execute run_pipeline.sh with your chat as an argument.
4. Open result (will be in Exports_whatsapp) with a browser and enjoy the graphs.

If you're crazy enough to try this without bash, look at the run_pipeline.sh script and try to follow the steps there.

TROUBLESHOOTING:
Most likely the preprocessing messed something up. I will improve it with time and hopefully it will be better with time.