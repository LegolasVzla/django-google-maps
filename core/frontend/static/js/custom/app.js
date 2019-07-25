var clickedSpotsArray = [];
var spotData = {};
var temporalLatLng = {}

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

// Function to set a position from click user interaction or default position
function spotGetModal(defaultLat,defaultLng) {

	var latitude = null, length = null; 

	// User already clicked a point
	if(Object.keys(temporalLatLng).length > 0){
		latitude = temporalLatLng["latitude"];
		length = temporalLatLng["length"]
		//console.log("I already choose a point",temporalLatLng)
	}else{
		//console.log("I didn't choose a point")
		latitude = defaultLat;
		length = defaultLng
	}

	$.ajax({
	    url:'/spot/',
	    type: 'POST',
	    data: {
	      method: "get",
	      lat: latitude,
	      lng: length
	 },success: function showAnswer(data) {
	  	if (data.code==200) {

		  	spotData = {};

			// Get information about the current place
			latlng = new google.maps.LatLng(latitude,length);
		  	reverse_geocoding(latlng);
		    //console.log("success",data);

		    // Send data to the modal inputs
		    $("#spotCreateShowModal").click(function(e){

		      console.log("close modal",data)
		      e.preventDefault();
		     // $("#spotCreateShowModal").modal('show');
		    });
		}else{
		    console.log('Error to load modal');
		  }
		}
	})

}

// Function to get the spot Id requested by the user and return the spot information
function spotEditModal(spotId) {

	$.ajax({
	    url:'/spot/editSpotModal/',
	    type: 'POST',
	    data: {
	      method: "editSpotModal",
	      spot_id: spotId
	 },success: function showAnswer(data) {
	  	if (data.code==200) {

		    // Send data to the modal inputs
		    $(".spotName").text(data.spotName)
		    $("#placeNameToEdit").val(data.spotName)
		    $("#cityToEdit").val(data.city)
		    $("#countryToEdit").val(data.country)
		    $("#countryCodeToEdit").val(data.country_code)
		    $("#latitudeToEdit").val(data.lat)
		    $("#lengthToEdit").val(data.lng)
		    $(".spotIdToEdit").text(data.id)

		}else{
		    console.log('Error to load modal');
		  }
		}
	})
}

// Function to edit the spot information
function spotUpdate(spotIdToEdit){

	console.log($('#spotUpdateShowModal'+spotIdToEdit).attr("data-spotId"))

	if (jQuery.isEmptyObject($("#placeName").val())) {
        alertify.error('Please provide a new name for the place');
		return;
	}else{
		spotData["placeName"]=$("#placeName").val();

		spotData['method'] = "update"
		$.ajax({
		    url:'/spot/update/',
		    type: 'POST',
		    data: spotData,success: function showAnswer(data) {
			  if (data.code==200) {
			    //console.log("success",data);
		        alertify.success('Spot saved successfully');
		        var delayInMilliseconds = 2000; // 2 second
		        setTimeout(function() {
		          location.reload(true);
		        }, delayInMilliseconds);
			  }else{
			    console.log('Error, status:',data.code);
			  }
			}
		})
	}
}


// Function to remove the spot requested by the user
function spotRemoveConfirmation(spotId){

  var r = confirm("¿Are you sure to remove this place?");
  if (r == true) {
    console.log('');
  } else {
    return;
  }
  $.ajax({
    url:'/spot/delete',
    type: 'PUT',
    data: {
      method: "delete",
      spot_id: spotId,
  },
    success: function showAnswer(data) {
      if (data.code==200) {

        alertify.success("The spot: '" +data.placeName+ "' was deleted successfully");
        var delayInMilliseconds = 2000; // 2 second
        setTimeout(function() {
          location.reload(true);
        }, delayInMilliseconds);
      }else{
        alertify.error('An error happened removing the spot, please try again.');
      }

    }
  });
};

// Function to select a spot and get geolocation values
function spotSelect(location){

	temporalLatLng = {}
	// Define a new marker in the clicked position
	var spot = new google.maps.Marker({
		position: location,
		map: map,
		// animation: google.maps.Animation.DROP
	});

	console.log("latitude: ", location.lat());
	console.log("longitud: ", location.lng());
	temporalLatLng["latitude"] = location.lat()
	temporalLatLng["length"] = location.lng()

	for (var i in clickedSpotsArray) {
		clickedSpotsArray[i].setMap(null);
	}

	clickedSpotsArray.push(spot);
}

// Function to save the spot information
function spotCreate(defaultLat,defaultLng){

	if (jQuery.isEmptyObject($("#placeName").val())) {
        alertify.error('Please provide a place name');
		return;
	}else{
		spotData["placeName"]=$("#placeName").val();

		spotData['method'] = "create"
		$.ajax({
		    url:'/spot/create/',
		    type: 'POST',
		    data: spotData,success: function showAnswer(data) {
			  if (data.code==200) {
			    //console.log("success",data);
		        alertify.success('Spot saved successfully');
		        var delayInMilliseconds = 2000; // 2 second
		        setTimeout(function() {
		          location.reload(true);
		        }, delayInMilliseconds);
			  }else{
			    console.log('Error, status:',data.code);
			  }
			}
		})
	}
}

// Set custom user spots
function spotNearBy(latitude,longitude) {

	console.log("coordinates:",latitude,longitude)
	$.ajax({
	    url:'/spot/nearby/',
	    type: 'POST',
	    data: {
	      method: "get_nearby",
	      lat: latitude,
	      lng: longitude
	 },success: function showAnswer(data) {
	  if (data.code==200) {

		// console.log("array of nearby places:",data.nearby)
        var delayInMilliseconds = 2000; // 2 second

		var shape = {
		    coord: [1, 1, 1, 20, 18, 20, 18 , 1],
		    type: 'poly'
		};

		var clickedSyCustomSpotsArray = []

		var mySpotList = data.nearby
		var location;
		var customUserSpot;

		for (var i=0; i<mySpotList.length; ++i) {

			location = new google.maps.LatLng(mySpotList[i].lat,mySpotList[i].lng);

			customUserSpot = new google.maps.Marker({
			    icon: '/static/media/place_icon.png',
			    shape: shape,
			    position: location,
			    map: map
			});

			clickedSyCustomSpotsArray.push(customUserSpot);
		}

	  }else{
        alertify.error('Not found own nearby places');
	  }
	}
	})
	
}

// Call when you APP gets the lat and long of the user
function load_map(defaultLat,defaultLng){
	console.log(defaultLat,defaultLng)

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

	// Adding listener click
	map.addListener('click',function(event){
		//console.log(event);
		console.log("HE LLAMADO A SELECT SPOT!!!!",event.latLng)
		spotSelect(event.latLng);
	});

	var spot = new google.maps.Marker({

		// default position
		position: new google.maps.LatLng(defaultLat,defaultLng),
		map: map,
		title: "My Spot"
	});

	clickedSpotsArray.push(spot);

}

