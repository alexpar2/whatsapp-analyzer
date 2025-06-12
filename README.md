This tool has been designed for whatsapp chats in European Spanish (the whole codebase is also in spanish). 
Not recommended for any other language unless you want to spend a good deal of time messing with the preprocessing.
CURRENTLY ONLY SUPPORTS THE ANDROID EXPORT FORMAT, NOT THE IOS ONE.

WHAT YOU NEED:
- An exported android whatsapp chat in txt
- python
- a bash terminal
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
3. Optional: Personalize your nickname_mapping.csv file for more precise results in some stats.
4. Execute run_pipeline.sh with your chat as an argument.If your chat is individual, then put -i as an initial argument, so that mention statistics are not created (could lead to error)
5. Open result (will be in Exports_whatsapp) with a browser and enjoy the graphs.

EXTRA RECOMENDATIONS:
- The mentions statistics work with the contact names. IF your contact name isn't how you usually refer to that contact, then you will need to di a nickname mapping file. That is, a simple csv with the column "original" and "nombre". Under original, you write the contact name. Under nombre, you write the real name of the person (or how you usually call them.)

- In the line graphs, especially the normalized ones, remove the outliers (people who have chatted very little) for less noisy data.You can do so by clicking on their name in the interactive graph.


TROUBLESHOOTING:
Most likely the preprocessing messed something up. I will improve it with time and hopefully it will be better with time.

FUTURE IMPROVEMENTS:
Might add sentence transformers and sentiment analysis but that will dramatically increase processing time.