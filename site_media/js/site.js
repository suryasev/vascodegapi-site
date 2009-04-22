$(document).ready(function() {
    $("#menu ul li:not(.selected)").hover(
        function() {
            $(this).animate({backgroundColor: '#BA8C5D', color: '#ffffff'}, 'fast');
            $(this).find('a').animate({backgroundColor: '#BA8C5D', color: '#ffffff'}, 'fast');
        },
        function() {
            $(this).animate({backgroundColor: '#ffffff', color: '#333333'}, 'fast');
            $(this).find('a').animate({backgroundColor: '#ffffff', color: '#333333'}, 'fast');
        }
    );
    
    
    
    $("#signup-button").hover(
        function() {
            $('#signup-button').animate(            {backgroundColor: '#77c464', color: '#000000'}, {queue: false, duration: 400});
            $('#signup-button div').animate(        {backgroundColor: '#7fd16b', color: '#000000'}, {queue: false, duration: 400});
            $('#signup-button div div').animate(    {backgroundColor: '#87de71', color: '#000000'}, {queue: false, duration: 400});
            $('#signup-button div div div').animate({backgroundColor: '#8feb78', color: '#000000'}, {queue: false, duration: 400});
        },
        function() {
            $('#signup-button').animate(            {backgroundColor: '#70b75e', color: '#555555'}, {queue: false, duration: 400});
            $('#signup-button div').animate(        {backgroundColor: '#77c464', color: '#555555'}, {queue: false, duration: 400});
            $('#signup-button div div').animate(    {backgroundColor: '#7fd16b', color: '#555555'}, {queue: false, duration: 400});
            $('#signup-button div div div').animate({backgroundColor: '#87de71', color: '#555555'}, {queue: false, duration: 400});
        }
    );


});

    