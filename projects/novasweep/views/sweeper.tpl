<html>
<head>
<title>Main</title>
<script src="/static/jquery-1.8.3.min.js" type="text/javascript"></script>
<script src="/static/jquery.utils.min.js" type="text/javascript"></script>
<script src="/static/moment.min.js" type="text/javascript"></script>
<link rel="stylesheet" href="/static/jquery.utils.css" type="text/css">
<style>
 .chhead {
   font-weight: bold;
 }
 table {
   border: 1px solid black;
 }
 td
 {
    text-align: center;
 }
 .warning {
   color: red;
   font-weight: bold;
 }
 #feedback {
   width: 500;
   text-align: left;
 }
.modal {
    display:    none;
    position:   fixed;
    z-index:    1000;
    top:        0;
    left:       0;
    height:     100%;
    width:      100%;
    background: rgba( 255, 255, 255, .8 ) 
                url('/static/loading.gif') 
                50% 50% 
                no-repeat;
}

/* When the body has the loading class, we turn
   the scrollbar off with overflow:hidden */
body.loading {
    overflow: hidden;   
}

/* Anytime the body has the loading class, our
   modal element will be visible */
body.loading .modal {
    display: block;
}
</style>
<script>
   var okparams = true;
   var feedback;

   $(document).ready(function () {
      var stepsdiv = $("#stepnum");
      var submitbtn = $("#submit");
      feedback = $("#feedback");
      var triggerbtn = $("#sendtrigger");

      var settings = {sfreq0: 100,
                      sfreq1: 100,
                      ffreq0: 110,
                      ffreq1: 110,
                      stepsize: 1,
                      totaltime: 1,
                      repeat: true,
                     };


       $("body").on({
          ajaxStart: function() { 
             $(this).addClass("loading"); 
         },
            ajaxStop: function() { 
              $(this).removeClass("loading"); 
         }    
      });
      var message = function(text) {
          feedback.html(moment().format("HH:mm:ss.SSS") + " <strong>"+text+"</strong><br>" +feedback.html());
      };
      message("Page loaded");

      $('#sendtrigger').click( function() {
           $.ajax({
                url: '/trigger'
           }).done(function(data) {
                  message('Triggered repeat');
           });

      });

      $('.setting').change(function() {
         var id = this.id;
         var obj = this;
         var value;
         if (id == "repeat") {
             value = $("#"+id).is(':checked');
             if (value) {
                triggerbtn.attr('disabled', 'disabled');
             } else {
                triggerbtn.removeAttr('disabled');
             };
         } else {
             value = parseFloat(this.value);
         }
         settings[id] = value;
         var numsteps = Math.floor(settings.totaltime / settings.stepsize * 10000) + 1;
         if (numsteps > 16384) {
            okparams = false;
            stepsdiv.addClass("warning");
            submitbtn.attr('disabled','disabled');
         } else {
            okparams = true;
            stepsdiv.removeClass("warning");
            submitbtn.removeAttr('disabled');
         };
         stepsdiv.html(numsteps+" steps");
      });

      $('#settings').submit(function() {
         if (okparams) {
           $.ajax({
                url: '/sequence',
                type: 'POST',
                data: settings
           }).done(function(data) {
                  if (data.result == 'OK') {
                     totaltime = parseFloat(data.totaltime).toPrecision(2);
                     message('Sweep parameters sent ('+totaltime+'s)');
                  } else {
                     message('Update error.... :(')
                  }
            });
         };
         return false;
      });

   });
</script>
</head>
<body>

<center>

<h2>Novatech Frequency Sweep</h2>
<form id="settings" action="">
<table>
  <tr>
    <td></td>
    <td>CH0</td>
    <td>CH1</td>
  </tr>
  <tr>
    <td>Start Frequency (MHz)</td>
    <td><input class="setting" id="sfreq0" name="sfreq0" type="number" min="0.1" max="171" step="0.0000001" value="100"></input></td>
    <td><input class="setting" id="sfreq1" name="sfreq1" type="number" min="0.1" max="171" step="0.0000001" value="100"></input></td>
  </tr>
  <tr>
    <td>Final Frequency (MHz)</td>
    <td><input class="setting" id="ffreq0" name="ffreq0" type="number" min="0.1" max="171" step="0.0000001" value="110"></input></td>
    <td><input class="setting" id="ffreq1" name="ffreq1" type="number" min="0.1" max="171" step="0.0000001" value="110"></input></td>
  </tr>
  <tr>
    <td>Time step size N<br>(where N as in Nx100us, 1..254)</td>
    <td colspan=2><input class="setting" id="stepsize" type="number" name="stepsize" min="1" max="254" step="1" value="1"></input></td>
  </tr>
  <tr>
    <td>Total time in seconds</td>
    <td colspan=2><input class="setting" id="totaltime" type="number" name="totaltime" min="0.0001" step="0.0001" max="200" value="1"></input><br><div id="stepnum">10001 steps</div></td>
  </tr>
  <tr>
    <td>Repeat</td>
    <td colspan=2><input class="setting" id="repeat" type="checkbox" name="repeat" checked></input></td>
  </tr>
  <tr>
    <td></td>
    <!-- <td><input class="setting" id="triggered" type="checkbox" name="triggered"></input></td> -->
    <td><button id="sendtrigger" type="button" disabled>Send trigger</button></td>
    <td></td>
  </tr>
  <tr>
    <td colspan=2></td>
    <td><input id="submit" type="submit" value="Send parameters / Run sweep"></input></td>
  </tr>
</table>
</form>

<h3>Messages:</h3>
<div id="feedback"></div>

</center>

<div class="modal"><!-- Place at bottom of page --></div>
</body>
</html>
