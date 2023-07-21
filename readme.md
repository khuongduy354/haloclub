# Karaoke Room Web App 
### Tech Stack 
- Django 
- Channels (Websocket) 
- React.js
- Agora.IO 
- Youtube API

### Apps Description 
An app where you can join into a room, select song and sing in turn. You can  video call and chat in realtime. There's a user-based rating features for singers.  

- Real-time video call and chat 
- Search videos directly from youtube 
- Singer's voice and Song got synced across the room 
- Fun Turn-based singing and Rating mechanics 

### Detailed  
- Enter room name, username and join room. 
- When joined, video call is connected automatically.
- People can search song through youtube (embedded in the app), first one select song is the singer, then the order of who is singing next is randomized. 
- If singer wants to end the singing, press the button, all the user is alerted, then asked to rate the performance based on a scale of 100. 
- After all users rated, alert the singer score, and announce the next singer. Only the specified singer can select song and start singing. 
- Just repeat like above til the rating process.
- After everybody in the room has sung, announcing the game is finished, and the winner as long as his/her scores. 

### Future features 
- Add a randomize list of quotes to congratulates the winner 
- The chat is not implemented yet
- Show leaderboards
- Redis instead of in memory 
- More mechanics: A.I based rating, singing challenge, duet,...

### Issues 
- fix connnect new user = startedSinging false 
- typing ?
- disconnect cleanup


