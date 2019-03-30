var mysql = require('mysql');
var express = require('express');
var session = require('express-session');
var bodyParser = require('body-parser');
var path = require('path');
var handlebars = require('express-handlebars').create({ defaultLayout:'main' });

var connection = mysql.createConnection({
	host     : 'localhost',
	user     : 'root',
	password : 'Monkeydude',
	database : 'nodelogin'
});

var app = express();

app.engine('handlebars', handlebars.engine);
app.set('view engine', 'handlebars');
app.use(express.static('public'));

//app.set('views', __dirname + '/Client/views');
//app.set('view engine', 'hbs')


app.use(session({
	secret: 'secret',
	resave: true,
	saveUninitialized: true
}));
app.use(bodyParser.urlencoded({extended : true}));
app.use(bodyParser.json());

app.get('/', function(request, response) {
	
	if (request.session.loggedin) {
		
        response.redirect('/home');
        console.log(request.session.username+' is now accessing dashboard without logging in');
	}
	else{
	response.render('login');
	}

});

app.get('/register', function(request, response) {
	//response.sendFile(path.join(__dirname + '/Client/Login/login.html'));
	response.render('register');


});

app.post('/auth', function(request, response) {
	var username = request.body.username;
	var password = request.body.password;
	if (username && password) {
        console.log(username+password);
       
       
        connection.query('SELECT * FROM accounts WHERE username = ? AND password = ?', [username, password], function(error, results, fields){
            console.log(results);
            if (results.length > 0) {
				request.session.loggedin = true;
				request.session.username = username;
				response.redirect('/home');
			} else {
				response.send('Incorrect Username and/or Password!');
			}			
			
        });
	} else {
		response.send('Please enter Username and Password!');
	
	}
});

app.get('/home', function(request, response) {
	if (request.session.loggedin) {
		var data = {
			user: request.session.username,
			type: 'Patient'
		 };
        response.render('homepatient', data);
        console.log(request.session.username+'is now accessing dashboard');
	} else {
		response.send('Please login to view this page!');
	}
	
});

app.get('/profile', function(request, response) {
	if (request.session.loggedin) {
		var data = {
			user: request.session.username,
			type: 'Patient'
		 };
        response.render('profile', data);
        console.log(request.session.username+'is now accessing dashboard');
	} else {
		response.redirect('/');
	}
	
});


app.listen(3000);