var output = Array()
var db;
var nonce = 0;
var enctime = 0;
var objstore;

function initDB(){
    var request = window.indexedDB.open("PuckAerospace");
    request.onerror = function(event) { console.log(event.target.errorCode) }
    request.onsuccess = function(event) { db = event.target.result; addDataPoint("foo", "Bar")}
    request.onupgradeneeded = function(event) {
        db = event.target.result;
        var objectStore = db.createObjectStore("puck", {keyPath:"name"});
        objectStore.transaction.oncomplete = function(event) {
            objectStore = db.transaction("puck", "readwrite").objectStore("puck");
            document.cookie.split(';').forEach(function(datapoint) {
                console.log("storing: " + datapoint)
                var foo = datapoint.trim().split('=')
                var obj = {"name":foo[0], "value":foo[1]}
                objectStore.add(obj);
            });
        };
    }
}

function addDataPoint(key, value){
    console.log("Attempting to add: " + key + ":" + value)
    db.transaction("puck", "readwrite").objectStore("puck").add({"name":key, "value": value}).onerror = function(event){
        console.log("error: "+event.target.errorCode)
        console.log(event)
    };
}

function stepSatContact(){
    var objstore = db.transaction("puck", "readwrite").objectStore("puck");
    var request = objstore.get("nonce");
    request.onerror = function(event){
        addDataPoint("nonce", "badnonce")
        nonce = "badnonce"
    }
    request.onsuccess = function(event){
        try {
            nonce = event.target.result.value
        } catch (error) {
            addDataPoint("nonce", "badnonce")
            nonce = "badnonce"
        }
        if(nonce == undefined){
            addDataPoint("nonce", "badnonce")

        }
    }
    db.transaction("puck").objectStore("puck").get("enctime").onsuccess = function(event){
        enctime = event.target.result.value
    }

    db.transaction("puck").objectStore("puck").get("nonce").onsuccess = function(event){
        nonce = event.target.result.value
    }

    var httpreq = new XMLHttpRequest();
    httpreq.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200){
            var resp = JSON.parse(this.responseText)
            output.push(resp.message)
            // var request3 = objstore.get("nonce");
            db.transaction("puck", "readwrite").objectStore("puck").get("nonce").onsuccess = function(event){
                data = event.target.result;
                data.value = resp.nonce;
                db.transaction("puck", "readwrite").objectStore("puck").put(data)
                nonce = data.value;
            }
        }
    }
    // httpreq.withCredentials = true;
    var formdata = new FormData();

    formdata.append("enctime", enctime);
    formdata.append("nonce", nonce);
    httpreq.open("POST", "/take_step");
    // httpreq.setRequestHeader("Content-type", "application/json")
    httpreq.send(formdata)
}

function dumpOutput(){
    // console.log("Dumping")
    var target = document.getElementById("output");
    while(output.length > 0){
        target.innerText += "\n" + output.shift();
    }
}

function countDownToEndOfContact(){
    console.log("cdref")
    var los_arr = document.cookie.split(';')
    var los = 0
    los_arr.forEach(element => {
        console.log(element)
        local = element.trim().split('=')[0]
        if (local=='endtime'){
            los = element.trim().split('=')[1]
        }
    })
    var target = document.getElementById("endOfTime")
    var repr = new Date(los * 1000)
    var now = new Date()
    if(now > repr){
        target.innerText = "OUT OF TIME"
        return
    }
    repr = new Date(repr - now)
    target.innerText = repr.getMinutes() + ":" + repr.getSeconds()
}