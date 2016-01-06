/* PAGE LAYOUT --------------------------------*/
body {
    margin: 0; 
    padding: 0;
    font-family: "Myriad Pro", "Lucida Grande", Tahoma, Verdana, Arial, sans-serif;
    height: 100%; 
    background-color: #E9E9E9;
    font-size: 110%;
}
body #wrapper { 
    background-color: white; 
    min-height: 600px;
    margin-top: -15px;
    margin-bottom: 35px; 
    margin-left: 230px;
    margin-right: 25px;
    padding: 20px;
    font-size: 100%;
	border-radius: 20px;
    border: 7px solid #cecece;
    border: 7px solid rgba(0,0,0,.05);
    background: #fff;
    background-clip: padding-box;
    box-shadow: 0 0 2px rgba(0, 0, 0, .5);
}

header {
  display: block;
  height: 100px;
  padding: 10px 35px;
}

.logo {
  display: inline-block;
  float: left;
  height: 90px; 
}

#subj {
  display: inline-block;
  padding-top: 10px;
  float: right;
  text-align: right;
}

#timestamp {
  padding-top: 30px;
}

h1 {
    text-transform: uppercase;
    text-align: center;
    color: #666;
    margin: 0 0 30px 0;
    letter-spacing: 4px;
    font: normal 26px/1 Verdana, Helvetica;
    position: relative;
}

h1:after, 
h1:before {
    background-color: #777;
    content: "";
    height: 1px;
    position: absolute;
    top: 15px;
    width: 120px;   
}

h1:after {      
    right: 70px;
}

h1:before {
    background-image: linear-gradient(right, #777, #fff);
    left: 65px;
}

/* VERTICAL MENU ------------------------------*/
/*http://aceinfowayindia.com/blog/2009/07/simple-verticale-menu-tutorial*/
#nav ul {
  margin:0;
  padding:0;
  list-style-type:none;
}

#navwrap {
  float:left;
  position: fixed;
  left: 10px;
  top: 150px;
}

#nav ul li {
  display: inline; /*IE 6*/
}

#nav ul li a {
  display:block;
  background:#E9E9E9;
  width:170px;
  text-decoration:none;
  padding:4px/*padding for top, bottom*/ 7px /*padding for left, right*/;
  border-bottom:1px solid #cccccc;
  border-left:5px solid #333333;
  color:#333333;
}

#nav ul li a:hover {
  border-left-color:#0099FF;
  color:#0066FF;
  background:#c4c4c4;
}

/* TABLE -------------------------------------*/
table{
    background-color:white;
    text-align:center;
    margin-left:auto;
    margin-right:auto;}

.large_view{
    width:95%;
}

/* IMAGE ------------------------------------*/
object{width:80vw;}

/*version.xml*/
toad {padding:10px;}

application {
    display:table;
    padding:5px;
    margin: 0px auto;

}

software {display: table-row; }

name {
    display:inline-block;
    font-weight:bold;
    display: table-cell;
    text-align:right;
}

name:after {
             content: ":";
}


hostname:before {
content: "hostname: ";
        font-weight:bold;
}

toadname:before {
content: "toadname: ";
        font-weight:bold;
}

uname:before {
  content: "uname: ";
  font-weight:bold;
}


hostname:after {
  display:block;
  content: "";
}

toadname:after {
  display:block;
  content: "";
}

uname:after {
  display:block;
  content: "";
}

version {
      padding:5px;
      display: table-cell;
      text-align:left;
}

server {
        border: 1px solid;
        margin: 0px auto;
        display: table;
        align: left;
        text-align: left;
        margin-top: 15px;

}
softwares {
        margin: 0px auto;
        display: table;
        align: center;
        margin-top: 15px;
}
