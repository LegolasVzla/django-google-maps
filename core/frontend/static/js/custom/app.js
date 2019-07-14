var spotsArray = [];

// Function to add spots
function addSpots(location){

	var spot = new google.maps.Marker({
		position: location,
		map: map,
		// animation: google.maps.Animation.DROP
	});

	console.log("latitude: ", location.lat());
	console.log("longitud: ", location.lng());
	for (var i in spotsArray) {
		spotsArray[i].setMap(null);
	}

	spotsArray.push(spot);
}

// Call when you APP gets the lat and long of the user
function load_map(){

	var googleOptions = {
		zoom:15,
		// default location of the map, get the Location of the user
		center: new google.maps.LatLng(10.4823307,-66.861713),
		mapTypeControl: true,
		/*
		mapTypeControlOptions: {
		  style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
		  position: google.maps.ControlPosition.TOP_LEFT
		},*/
		// map type
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};

	map = new google.maps.Map(document.getElementById('gmap_canvas'), googleOptions)

	// Adding listener click
	map.addListener('click',function(event){
		//console.log(event);
		addSpots(event.latLng);
	});

	var spot = new google.maps.Marker({

		// default position
		position: new google.maps.LatLng(10.4823307,-66.861713),
		map: map,
		title: "My Spot"
	});

	spotsArray.push(spot);

	var shape = {
	    coord: [1, 1, 1, 20, 18, 20, 18 , 1],
	    type: 'poly'
	};

	var mySpotList = [{x:10.48218098377708,y:-66.86277687549591},{x:10.480189704841623,y:-66.86086177825928},{x:10.491156086040085,y:-66.86255693435669}];
	var currentSpot;
	var mySpotList;

	for (var i=0; i<mySpotList.length; ++i) {

		currentSpot = new google.maps.LatLng(mySpotList[i].x,mySpotList[i].y);

		mySpotsArray = new google.maps.Marker({
		    icon: '/static/media/place_icon.png',
		    shape: shape,
		    position: currentSpot,
		    map: map
		});

		spotsArray.push(mySpotsArray);

	}


}

