var fs = require('fs')



// read user.json format and parse it into user  
const dataBuffer = fs.readFileSync('includes/user.json')
const dataJson = dataBuffer.toString()
const user = JSON.parse(dataJson)




// Practice setting value 
const name= 'Atharv'
user.name ='Atharv'


// Write back unique JSON object 
const userJSON = JSON.stringify(user)
fs.writeFileSync('Users/'+name+'.json', userJSON)