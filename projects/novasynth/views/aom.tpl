<html>
<head>
<title>Main</title>
<script src="/static/jquery.min.js" type="text/javascript"></script>
<script src="/static/jquery.utils.min.js" type="text/javascript"></script>
<link rel="stylesheet" href="/static/jquery.utils.css" type="text/css">
<style>
 .chhead {
   font-weight: bold;
 }
 table {
   border: 1px solid black;
 }
</style>
<script>

   $(document).ready(function () {

     $('.chinfield').keypress(function(e){
        if(e.which == 13){
           var now = new Date();
           var displayTime = $.format('{H:02d}:{M:02d}:{S:02d}', {H: now.getHours(), M: now.getMinutes(), S: now.getSeconds()});
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

     $('.levelfield').keypress(function(e){
        if(e.which == 13){
           var now = new Date();
           var displayTime = $.format('{H:02d}:{M:02d}:{S:02d}', {H: now.getHours(), M: now.getMinutes(), S: now.getSeconds()});
           var channel = $(this).attr('name');
           var level = $(this).val();
           var url = "/setlevel/"+channel+"/"+level;
           $.post(url, function( msg ) {
                         var status = $.format('updating Channel {ch:d} to level {l:d}: {m}', {ch: channel, l: level, m: msg})
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
  <tr><td colspan=2 class="chhead">Channel 0:</td></tr>
  <tr><td>Frequency</td><td>Level(0-1024)</td></tr>
  <tr>
    <td>
      <input name="0" id="ch0in" class="chinfield">
    </td>
    <td>
      <input name="0" id="ch0lev" class="levelfield">
    </td>
  </tr>

  <tr><td colspan=2 class="chhead">Channel 1: </td></tr>
  <tr><td>Frequency</td><td>Level (0-1024)</td></tr>
  <tr>
    <td>
      <input name="1" id="ch1in" class="chinfield">
    </td>
    <td>
      <input name="1" id="ch1lev" class="levelfield">
    </td>
  </tr>

  <tr><td colspan=2 class="chhead">Channel 2: </td></tr>
  <tr><td>Frequency</td><td>Level (0-1024)</td></tr>
  <tr>
    <td>
      <input name="2" id="ch2in" class="chinfield">
    </td>
    <td>
      <input name="2" id="ch2lev" class="levelfield">
    </td>
  </tr>

  <tr><td colspan=2 class="chhead">Channel 3: </td></tr>
  <tr><td>Frequency</td><td>Level (0-1024)</td></tr>
  <tr>
    <td>
      <input name="3" id="ch3in" class="chinfield">
    </td>
    <td>
      <input name="3" id="ch3lev" class="levelfield">
    </td>
  </tr>
</table>

<div id="feedback"></div>

</center>

</body>
</html>
