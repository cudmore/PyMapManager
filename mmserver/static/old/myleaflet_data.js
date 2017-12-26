
myData = {}
myData.x = [100,200,300,400,500]
myData.y = [100,200,300,400,500]
myData.z = [1,2,3,4,5]

var bicycleRental = {
    "type": "FeatureCollection",
    "features": []
}

for (var i=0; i<myData.x.length; i++) {
    bicycleRental.features.push(
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    myData.x[i],
                    myData.y[i]
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "spine " + i
            },
            "id": i
        },
    )
}
console.log(bicycleRental)

var bicycleRental0 = {
    "type": "FeatureCollection",
    "features": [
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    104.9998241,
                    39.7471494
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "This is a B-Cycle Station. Come pick up a bike and pay by the hour. What a deal!"
            },
            "id": 51
        },
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    104.9983545,
                    59.7502833
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "This is a B-Cycle Station. Come pick up a bike and pay by the hour. What a deal!"
            },
            "id": 52
        },
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    104.9963919,
                    79.7444271
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "This is a B-Cycle Station. Come pick up a bike and pay by the hour. What a deal!"
            },
            "id": 54
        },
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    104.9960754,
                    99.7498956
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "This is a B-Cycle Station. Come pick up a bike and pay by the hour. What a deal!"
            },
            "id": 55
        },
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    104.9933717,
                    119.7477264
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "This is a B-Cycle Station. Come pick up a bike and pay by the hour. What a deal!"
            },
            "id": 57
        },
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    104.9913392,
                    139.7432392
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "This is a B-Cycle Station. Come pick up a bike and pay by the hour. What a deal!"
            },
            "id": 58
        },
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    104.9788452,
                    159.6933755
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "This is a B-Cycle Station. Come pick up a bike and pay by the hour. What a deal!"
            },
            "id": 74
        }
    ]
};
