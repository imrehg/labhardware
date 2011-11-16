<html>
<head>
<title>Main</title>
<script src="/static/jquery.min.js" type="text/javascript"></script>
<script src="/static/jquery.utils.min.js" type="text/javascript"></script>
<link rel="stylesheet" href="/static/jquery.utils.css" type="text/css">
<script>

   $(document).ready(function () {

     $('.chinfield').keypress(function(e){
        if(e.which == 13){
           var now = new Date();
           var displayTime = $.format('{H:0d}:{M:0d}:{S:0d}', {H: now.getHours(), M: now.getMinutes(), S: now.getSeconds()});
           var channel = $(this).attr('name');
           var frequency = $(this).val();
           var url = "/setfreq/"+channel+"/"+frequency;
           $.post(url, function( msg ) {
                         var status = $.format('updating Channel {ch:d} to {f:3.7f} MHz: {m}', {ch: channel, f: frequency, m: msg})
                         $("#feedback").html("<b>" + displayTime + "</b> : " +status + "</br>"+$("#feedback").html());
                       }
                 );
       }
      });
    });
</script>
</head>
<body>

<center>

<h2>Type in the desired frequency and press Enter.</h2>
<table>
  <tr><td>Channel 0: </td></tr>
  <tr>
    <td>
      <input name="0" id="ch0in" class="chinfield">
    </td>
  </tr>

  <tr><td>Channel 1: </td></tr>
  <tr>
    <td>
      <input name="1" id="ch1in" class="chinfield">
    </td>
  </tr>

  <tr><td>Channel 2: </td></tr>
  <tr>
    <td>
      <input name="2" id="ch2in" class="chinfield">
    </td>
  </tr>

  <tr><td>Channel 3: </td></tr>
  <tr>
    <td>
      <input name="3" id="ch3in" class="chinfield">
    </td>
  </tr>
</table>

<div id="feedback"></div>

</center>

</body>
</html>
