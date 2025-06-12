This tool has been designed for whatsapp chats in European Spanish (the whole codebase is also in spanish). 
Not recommended for any other language unless you want to spend a good deal of time messing with the preprocessing.

WHAT YOU NEED:
- An exported whatsapp chat in txt
- python
- a bash terminal if you don't want to execute the scripts yourself
- A browser that's not Firefox

HOW TO EXPORT A WHATSAPP CHAT
1. Go to the chat in your phone
2. Tap on the three dots in the upper right corner
3. Tap on "more"
4. Tap on "export chat"
5. Select the option that omits media

STEPS:
1. Move to the directory where the scripts are
2. Install requirements (python3 -m pip install -r requirements.txt)
3. Execute run_pipeline.sh with your chat as an argument.If your chat is individual, then put -i as an initial argument, so that mention statistics are not created (could lead to error)
4. Open result (will be in Exports_whatsapp) with a browser and enjoy the graphs.

If you're crazy enough to try this without bash, look at the run_pipeline.sh script and try to follow the steps there.

EXTRA RECOMENDATIONS:
The mentions statistics work with the contact names. IF your contact name isn't how you usually refer to that contact, then you will need to
go to the preprocessing script, and add to the nickname mapping your "translation".
In the line graphs, especially the normalized ones, remove the outliers (people who have chatted very little) for less noisy data.
You can do so by clicking on their name in the interactive graph.

TROUBLESHOOTING:
Most likely the preprocessing messed something up. I will improve it with time and hopefully it will be better with time.

FUTURE IMPROVEMENTS:
Might add a "individual" argument for the analysis script that leaves out group-only stats such as mentions.
Might add sentence transformers and sentiment analysis but that will dramatically increase processing time.