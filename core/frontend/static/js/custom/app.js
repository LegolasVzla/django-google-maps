var spotsArray = [];

// Function to add spots
function addSpots(location){

	var spot = new google.maps.Marker({
		position: location,
		map: map,
		// animation: google.maps.Animation.DROP
	});

	//console.log("location", location)
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

}