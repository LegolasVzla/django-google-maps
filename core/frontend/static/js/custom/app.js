var spotsArray = [];
var spotData = {};

// Function to get place information from latitude and lenght
function reverse_geocoding(location) {

	new google.maps.Geocoder().geocode({'latLng' : location}, function(results, status) {
	//console.log(results, status);
	    if (status == google.maps.GeocoderStatus.OK) {
	        if (results[1]) {
	            var country = null, countryCode = null, city = null, cityAlt = null;
	            var c, lc, component;

	            for (var r = 0, rl = results.length; r < rl; r += 1) {
	                var result = results[r];
	                if (!city && result.types[0] === 'locality') {
	                    for (c = 0, lc = result.address_components.length; c < lc; c += 1) {
	                        component = result.address_components[c];

	                        if (component.types[0] === 'locality') {
	                            city = component.long_name;
	                            break;
	                        }
	                    }
	                }
	                else if (!city && !cityAlt && result.types[0] === 'administrative_area_level_1') {
	                    for (c = 0, lc = result.address_components.length; c < lc; c += 1) {
	                        component = result.address_components[c];

	                        if (component.types[0] === 'administrative_area_level_1') {
	                            cityAlt = component.long_name;
	                            break;
	                        }
	                    }
	                } else if (!country && result.types[0] === 'country') {
	                    country = result.address_components[0].long_name;
	                    countryCode = result.address_components[0].short_name;
	                }

	                if (city && country) {
	                    break;
	                }
	            }

	            //console.log("City: " + city + ", City2: " + cityAlt + ", Country: " + country + ", Country Code: " + countryCode);
			    $("#city").val(city)
			    $("#country").val(country)
			    $("#countryCode").val(countryCode)
			    $("#latitude").val(location.lat())
			    $("#length").val(location.lng())

				spotData["city"]=city;
				spotData["country"]=country;
				spotData["countryCode"]=countryCode;
				spotData["latitude"]=location.lat();
				spotData["length"]=location.lng();
			    console.log("Spot data",spotData)

	        }
	    } else {
	    	document.getElementById('error').innerHTML = "Error Status: " + status;
	    }
	})

}

function get_place_information() {

	var latitude = null, length = null; 

	// User already clicked a point
	if(spotsArray.length > 0){
		latitude = spotData["latitude"];
		length = spotData["length"]
	}else{
		latitude = defaultLat;
		length = defaultLng
	}

	// Get information about the current place
	latlng = new google.maps.LatLng(latitude,length);
	reverse_geocoding(latlng);

}

// Function to select spots and get geolocation values
function selectSpot(location){

	var spot = new google.maps.Marker({
		position: location,
		map: map,
		// animation: google.maps.Animation.DROP
	});

	console.log("latitude: ", location.lat());
	console.log("longitud: ", location.lng());

	$.ajax({
	    url:'/index/',
	    type: 'POST',
	    data: {
	      lat: location.lat(),
	      lng: location.lng()
	 },success: function showModal(data) {
	  if (data.code==200) {

	  	spotData = {};
	  	reverse_geocoding(location);

	    console.log("success",data);

	    $("#placeShowModal").click(function(e){
	      console.log("close modal",data)
	      e.preventDefault();
	     // $("#placeShowModal").modal('show');
	    });
	  }else{
	    console.log('Error to load modal');
	  }
	}
	})

	for (var i in spotsArray) {
		spotsArray[i].setMap(null);
	}

	spotsArray.push(spot);
}

// Function to select spots and get geolocation values
function addSpot(defaultLat,defaultLng){



	if ($("#placeName").val()==undefined) {
	  	spotData = {};
        alertify.error('1: Please provide a place name');
		console.log("Name is required!")
	    var delayInMilliseconds = 8000; // 2 second
	    setTimeout(function() {
	      location.reload(true);
	    }, delayInMilliseconds);

		return;
	}else{
		spotData["placeName"]=$("#placeName").val();

		$.ajax({
		    url:'/index/spotCreate/',
		    type: 'POST',
		    data: spotData,success: function showAnswer(data) {
		      console.log('spot data save susscessfully',data);
			  if (data.code==200) {
			    console.log("success",data);
		        alertify.success('Spot saved susscessfully');
		        var delayInMilliseconds = 8000; // 2 second
		        setTimeout(function() {
		          location.reload(true);
		        }, delayInMilliseconds);
			  }else if (data.code==406) {
	  	        alertify.error('Please set a place first');
			    console.log('Error');
			  	spotData = {};

			  }else{
	  	        alertify.error('2: Please provide a place name');
		        var delayInMilliseconds = 8000; // 2 second
		        setTimeout(function() {
		          location.reload(true);
		        }, delayInMilliseconds);
			    console.log('Error');
			  	spotData = {};
			  }
			}
		})

	}


}

// Set custom user spots
function addCustomUSerSpots() {
	
	var shape = {
	    coord: [1, 1, 1, 20, 18, 20, 18 , 1],
	    type: 'poly'
	};

	var myCustomSpotsArray = []
	var mySpotList = [{x:10.48218098377708,y:-66.86277687549591},{x:10.480189704841623,y:-66.86086177825928},{x:10.491156086040085,y:-66.86255693435669}];
	var location;
	var customUserSpot;

	for (var i=0; i<mySpotList.length; ++i) {

		location = new google.maps.LatLng(mySpotList[i].x,mySpotList[i].y);

		customUserSpot = new google.maps.Marker({
		    icon: '/static/media/place_icon.png',
		    shape: shape,
		    position: location,
		    map: map
		});

		myCustomSpotsArray.push(customUserSpot);

	}

}

// Call when you APP gets the lat and long of the user
function load_map(defaultLat,defaultLng){

	var googleOptions = {
		zoom:15,
		// default location of the map, get the Location of the user
		center: new google.maps.LatLng(defaultLat,defaultLng),
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

	addCustomUSerSpots();

	// Adding listener click
	map.addListener('click',function(event){
		//console.log(event);
		console.log("HE LLAMADO A SELECT SPOT!!!!",event.latLng)
		selectSpot(event.latLng);
	});

	var spot = new google.maps.Marker({

		// default position
		position: new google.maps.LatLng(defaultLat,defaultLng),
		map: map,
		title: "My Spot"
	});

	spotsArray.push(spot);

}

