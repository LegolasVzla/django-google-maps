var clickedSpotsArray = [];
var spotData = {};
var temporalLatLng = {}
var firstClick = false;
var locationAux = null;
var temporalSpotToEdit = null;

// Function to get place information from latitude and lenght
function reverse_geocoding(location) {

	new google.maps.Geocoder().geocode({'latLng' : location}, function(results, status) {
	//console.log(results, status);
	    if (status == google.maps.GeocoderStatus.OK) {
	        if (results[1]) {
	            var country = null, countryCode = null, city = null, cityAlt = null, postal_code = null;
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

	                }
	                else if (!postal_code && result.types[0] === 'postal_code') {
	                    for (c = 0, lc = result.address_components.length; c < lc; c += 1) {
	                        component = result.address_components[c];

	                        if (component.types[0] === 'postal_code') {
	                            postal_code = component.long_name;
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

	            //console.log("City: " + city + ", City2: " + cityAlt + ", Country: " + country + ", Country Code: " + countryCode + ", Postal code: " + postal_code);
			    $("#city").val(city)
			    $("#country").val(country)
			    $("#countryCode").val(countryCode)
			    $("#postalCode").val(postal_code)
			    $("#latitude").val(location.lat())
			    $("#length").val(location.lng())

				spotData["city"]=city;
				spotData["country"]=country;
				spotData["countryCode"]=countryCode;
				spotData["postalCode"]=postal_code;
				spotData["latitude"]=location.lat();
				spotData["length"]=location.lng();
			    //console.log("Spot data",spotData)

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
		//console.log("I already choose a point",temporalLatLng)
		latitude = temporalLatLng["latitude"];
		length = temporalLatLng["length"]
	}else{
		//console.log("I didn't choose a point")
		latitude = defaultLat;
		length = defaultLng
	}

	$.ajax({
	    url:'/spot/',
	    type: 'POST',
	    data: {
	      action: "get_spot_modal",
	      lat: latitude,
	      lng: length
	 },success: function showAnswer(data) {
	  	if (data.code==200) {

		  	spotData = {};

			/* This is another alternative instead of use geopy in backend
		  	Uncomment the below section if you want to use
		  	reverse_geocoding() function */

			// Get information about the current place
			//latlng = new google.maps.LatLng(latitude,length);

		  	// reverse_geocoding(latlng);

		    $("#country").val(data.data.place_information.country_name)
		    $("#countryCode").val(data.data.place_information.country_code)
		    $("#stateName").val(data.data.place_information.state_name)
		    $("#city").val(data.data.place_information.city_name)
		    $("#postalCode").val(data.data.place_information.postal_code)
		    $("#fullAddress").text(data.data.place_information.full_address)
		    $("#latitude").val(latitude)
		    $("#length").val(length)

			spotData["country"]=data.data.place_information.country_name;
			spotData["countryCode"]=data.data.place_information.country_code;
			spotData["state_name"]=data.data.place_information.state_name;
			spotData["city"]=data.data.place_information.city_name;
			spotData["postalCode"]=data.data.place_information.postal_code;
			spotData["fullAddress"]=data.data.place_information.full_address;
			spotData["latitude"]=latitude;
			spotData["length"]=length;
			//-------------------------------------

		    // Send data to the modal inputs
		    $("#spotCreateShowModal").click(function(e){

		      //console.log("close modal",data)
		      e.preventDefault();
		     // $("#spotCreateShowModal").modal('show');
		    });
		}else{
		    console.log('Error to load modal',data.code);
	        alertify.error('An error happened when loading this modal, please try again.');
		  }
		}
	})
}

// Function to save the spot information
function spotCreate(defaultLat,defaultLng){

	if (jQuery.isEmptyObject($("#placeName").val())) {
        alertify.error('Please provide a place name');
		return;
	}else{
		spotData["placeName"]=$("#placeName").val();
		spotData["tagList"]=$("#jQuerytagEditorModalGet").val()

		$.ajax({
		    url:'/spot/create/',
		    type: 'POST',
		    data: {
		    	action: "create_spot",
				country: spotData.country,
				countryCode: spotData.countryCode,
				state_name: spotData.state_name,
				city: spotData.city,
				postalCode: spotData.postalCode,
				fullAddress: spotData.fullAddress,
				latitude: spotData.latitude,
				length: spotData.length,
				placeName: spotData.placeName,
				tagList: spotData.tagList		    
			},success: function showAnswer(data) {
			  if (data.code==200) {
			    //console.log("success",data);
		        alertify.success('Spot saved successfully');
		        var delayInMilliseconds = 2000; // 2 second
		        setTimeout(function() {
		          location.reload(true);
		        }, delayInMilliseconds);
			  }else{
			    console.log('Error, status:',data.code);
		        alertify.error('An error happened saving the spot, please try again.');
			  }
			}
		})
	}
}

// Set custom user spots
function spotNearBy(latitude,longitude) {
	var latitude_aux = null, length_aux = null;

	if (firstClick) {
		latitude_aux = locationAux.lat()
		length_aux = locationAux.lng()
	}else{
		latitude_aux = latitude
		length_aux = longitude
	}
	//console.log("coordinates:",latitude_aux,length_aux)	

	$.ajax({
	    url:'/spot/nearby/',
	    type: 'POST',
	    data: {
	      action: "get_nearby_places",	    	
	      lat: latitude_aux,
	      lng: length_aux
		 },success: function showAnswer(data) {
			if (data.code==200) {

				var shape = {
				    coord: [1, 1, 1, 20, 18, 20, 18 , 1],
				    type: 'poly'
				};

				var clickedSyCustomSpotsArray = []

				var mySpotList = data.data.nearby
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

			}else if(data.code==204){
				alertify.error('Not found own nearby places');
			}else{
				console.log('Error to load modal');
				alertify.error('An error happened loading nearby places, please try again.');
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
	      action: "edit_spot_modal",
	      spot_id: spotId
	 },success: function showAnswer(data) {
	  	if (data.code==200) {

		    // Send data to the modal inputs
		    $(".spotName").text(data.spotName)
		    $("#placeNameToEdit").val(data.spotName)
		    $("#countryToEdit").val(data.country_name)
		    $("#countryCodeToEdit").val(data.country_code)
		    $("#stateToEdit").val(data.state_name)
		    $("#cityToEdit").val(data.city_name)
		    $("#postalCodeToEdit").val(data.postal_code)
		    $("#fullAddressToEdit").val(data.full_address)
		    $("#latitudeToEdit").val(data.lat)
		    $("#lengthToEdit").val(data.lng)
		    $(".spotIdToEdit").text(data.id)

		    $('#jQuerytagEditorModalEdit').tagEditor('addTag', data.tagList);

			//$('#jQuerytagEditorModalEdit').tagEditor({initialTags: data.tagList});
		    
		    /*
		    $('#remove_all_tags').click(function() {
		        var tags = $('#jQuerytagEditorModalEdit').tagEditor('getTags')[0].tags;
		        for (i=0;i<tags.length;i++){ $('#jQuerytagEditorModalEdit').tagEditor('removeTag', tags[i]); }
		    });
			*/

		    temporalSpotToEdit = data.id

		}else{
		    console.log('Error to load modal');
	        alertify.error('An error happened when loading this modal, please try again.');		    
		  }
		}
	})
}

// Function to edit the spot information
function spotUpdate(){

	if (jQuery.isEmptyObject($("#placeNameToEdit").val())) {
        alertify.error('Please provide a new name for the place');
	}else{
		spotData["name"]=$("#placeNameToEdit").val();
		spotData["spotId"] = temporalSpotToEdit
		temporalSpotToEdit = null

		//var newTags = $('#jQuerytagEditorModalEdit').tagEditor('getTags')[0].tags;
		//console.log("------New tag list:------",newTags)
		//spotData["newTagList"] =  newTags
		$.ajax({
		    url:'/spot/update/',
		    type: 'PUT',
		    data: spotData,success: function showAnswer(data) {
			  if (data.code==200) {
		        alertify.success('Spot saved successfully');
		        var delayInMilliseconds = 2000; // 2 second
		        setTimeout(function() {
		          location.reload(true);
		        }, delayInMilliseconds);
			  }else{
			    console.log('Error, status:',data.code);
			    alertify.error('Error updating the spot: ',data.placeName);
			  }
			}
		})
	}
}

// Function to remove the spot requested by the user
function spotRemove(spotId){
  var r = confirm("¿Are you sure to remove this place?");

  if (r == true) {
    console.log('');
  } else {
    return;
  }
  $.ajax({
    url:'/spot/delete',
    type: 'DELETE',
    data: {
      spot_id: spotId
  },
    success: function showAnswer(data) {
      if (data.code==200) {

        alertify.success("The spot: '" +data.data.placeName+ "' was deleted successfully");
        var delayInMilliseconds = 2000; // 2 second
        setTimeout(function() {
          location.reload(true);
        }, delayInMilliseconds);
      }else{
        alertify.error('An error happened removing the spot, please try again.');
      }

    }
  });
}

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

	locationAux = location;
	firstClick = true;
}

// Call when you APP gets the lat and long of the user
function load_map(defaultLat,defaultLng){
	console.log("latitude: ", defaultLat);
	console.log("longitud: ", defaultLng);

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