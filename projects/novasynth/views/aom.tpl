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

     $.get('/settings/', function(data) {
        for (var ch in data) {
              freq = data[ch].freq;
              $("#ch"+ch+"in").val(freq);
              amp = data[ch].amp;
              $("#ch"+ch+"lev").val(amp);
              phase = data[ch].phase;
              $("#ch"+ch+"ph").val(phase);
        }

     });

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

     $('.phasefield').keypress(function(e){
        if(e.which == 13){
           var now = new Date();
           var displayTime = $.format('{H:02d}:{M:02d}:{S:02d}', {H: now.getHours(), M: now.getMinutes(), S: now.getSeconds()});
           var channel = $(this).attr('name');
           var level = $(this).val();
           var url = "/setphase/"+channel+"/"+level;
           $.post(url, function( msg ) {
                         var status = $.format('updating Channel {ch:d} to phase {l:d}: {m}', {ch: channel, l: level, m: msg})
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

<h2>Type in the desired value and press Enter to set it.</h2>
<table>
  <tr><td colspan=3 class="chhead">Channel 0:</td></tr>
  <tr><td>Frequency</td><td>Level(0-1024)</td><td>Phase (0-16383)</td></tr>
  <tr>
    <td>
      <input name="0" id="ch0in" class="chinfield">
    </td>
    <td>
      <input name="0" id="ch0lev" class="levelfield">
    </td>
    <td>
      <input name="0" id="ch0ph" class="phasefield">
    </td>
  </tr>

  <tr><td colspan=3 class="chhead">Channel 1: </td></tr>
  <tr><td>Frequency</td><td>Level(0-1024)</td><td>Phase (0-16383)</td></tr>
  <tr>
    <td>
      <input name="1" id="ch1in" class="chinfield">
    </td>
    <td>
      <input name="1" id="ch1lev" class="levelfield">
    </td>
    <td>
      <input name="1" id="ch1ph" class="phasefield">
    </td>
  </tr>

  <tr><td colspan=3 class="chhead">Channel 2: </td></tr>
  <tr><td>Frequency</td><td>Level (0-1024)</td><td>Phase (0-16383)</td></tr>
  <tr>
    <td>
      <input name="2" id="ch2in" class="chinfield">
    </td>
    <td>
      <input name="2" id="ch2lev" class="levelfield">
    </td>
    <td>
      <input name="2" id="ch2ph" class="phasefield">
    </td>
  </tr>

  <tr><td colspan=3 class="chhead">Channel 3: </td></tr>
  <tr><td>Frequency</td><td>Level (0-1024)</td><td>Phase (0-16383)</td></tr>
  <tr>
    <td>
      <input name="3" id="ch3in" class="chinfield">
    </td>
    <td>
      <input name="3" id="ch3lev" class="levelfield">
    </td>
    <td>
      <input name="3" id="ch3ph" class="phasefield">
    </td>
  </tr>
</table>

<h3>Messages:</h3>
<div id="feedback"></div>

</center>

</body>
</html>
