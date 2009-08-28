#!/usr/bin/env python

import cgi

def main():
    form = cgi.FieldStorage()
    checked = ["", "", ""]
    func = 0
    funcname = "Sine"
    if (form.has_key("function")):
        if form["function"].value in ["0", "1", "2"]:
        func = int(form["function"].value)
          funcname = {
            0 : lambda : 'Sine',
            1 : lambda : 'Square',
            2 : lambda : 'Ramp'
          }[func]()
          checked[func] = "checked"
    if (form.has_key("currentfreq")):
        currentfreq = int(form["currentfreq"].value)
    else:
        currentfreq = 1000
    if (form.has_key("freq")):
       freq = int(form["function"].value)
       if freq == 1:
          multi = 0.8
       elif freq == 0:
          multi = 1.2
       else:
          multi = 1
       currentfreq = int(multi * currentfreq)


    if (not form.has_key("action")):
      file = "/srv/labauto/data/tricky"
      outp = open(file, "w")
      outp.write("%d,%d" %(currentfreq, func))
      outp.close()


    print "Content-type: text\html\n"
    print "<html>"
    print "<body>"
    print "<h1>Saved scope data:</h1>"
    print "<h4>Current setting : %d Hz, %s</h4>" %(currentfreq, funcname)
    print "<img src=/data/scope.png height=400><br>"

    print "\t\t<FORM METHOD = post ACTION = \
    \"/labauto\">\n"
    print "<INPUT type=\"hidden\" name=\"currentfreq\" value=\"%d\" >" % (currentfreq)
    print "<INPUT type=\"radio\" name=\"freq\" value=\"0\" > Increase Freqency<BR>"
    print "<INPUT type=\"radio\" name=\"freq\" value=\"1\" > Decrease Frequency<BR><br>"
    print "<INPUT type=\"radio\" name=\"function\" value=\"0\" %s> Sine<BR>" % (checked[0])
    print "<INPUT type=\"radio\" name=\"function\" value=\"1\" %s> Square<BR>" % (checked[1])
    print "<INPUT type=\"radio\" name=\"function\" value=\"2\" %s> Ramp<BR>" % (checked[2])
    print "\t<INPUT TYPE = submit VALUE = \"Enter\">\n"
    print "\t</FORM>\n"

    print "\t\t<FORM METHOD = post ACTION = \
    \"/labauto\">\n"
    print "<INPUT type=\"hidden\" name=\"function\" value=\"%d\" >" % (func)
    print "<INPUT type=\"hidden\" name=\"currentfreq\" value=\"%d\" >" % (currentfreq)
    print "<INPUT type=\"hidden\" name=\"action\" value=\"refresh\" >"
    print "\t<INPUT TYPE = submit VALUE = \"Refresh\">\n"
    print "\t</FORM>\n"

    print "</body></html>"

main()
