from PIL import ImageGrab, Image
from validate_email import validate_email
import thread, threading
import numpy as np
import cv2
import os
import time
import smtplib
import wx
import Queue


from view import View


MAILSERVER = smtplib.SMTP('outlook.office365.com', 587)
MAILSERVER.starttls()
MAILSERVER.ehlo()
MAILSERVER.login("info@atumsoft.com", "\"d~XsN*9;+<Ec:ZB")
FROMADDR = 'info@atumsoft.com'
TOADDR = ''
TEMPFILENAME = 'temp.png'
THRESHOLD = .2

MESSAGE = """From: %s
To: %s
Subject: Instrument Error

Software issue detected, your attention required.
"""


class Controller:
    def __init__(self):
        self.mainWindow = View(None)
        self.mainWindow.lblError.SetLabel('          ')
        self.mainWindow.timerScreenshot.Stop()

        self.mainWindow.Bind(wx.EVT_BUTTON, self.start, self.mainWindow.btnStart)
        self.mainWindow.Bind(wx.EVT_BUTTON, self.stop, self.mainWindow.btnStop)
        self.mainWindow.Bind(wx.EVT_CLOSE, self.shutdown)
        self.mainWindow.Bind(wx.EVT_TIMER, self.onTick, self.mainWindow.timerScreenshot)

        self.matchImage = cv2.imread(os.path.normpath('testImage.png'))
        self.resultQ = Queue.Queue()
        self.errorFound = False
        self.emailAddr = ''

    def show(self):
        self.mainWindow.Show()

    def start(self, event):
        self.emailAddr = self.mainWindow.txtEmail.GetValue()
        if not self.emailAddr: return
        if not validate_email(self.emailAddr):
            msgBox = wx.MessageDialog(self.mainWindow, 'Invalid Email Address: %s' % self.emailAddr, 'Invalid Input', wx.ICON_ERROR)
            msgBox.ShowModal()
            return

        self.mainWindow.txtEmail.Disable()
        self.mainWindow.lblError.SetBackgroundColour((0,255,0))
        self.mainWindow.Refresh()
        self.mainWindow.timerScreenshot.Start(10000)

    def stop(self, event):
        self.mainWindow.txtEmail.Enable()
        self.errorFound = False
        self.mainWindow.timerScreenshot.Stop()

    def shutdown(self, event):
        MAILSERVER.close()
        self.mainWindow.timerScreenshot.Stop()
        event.Skip()

    def onTick(self, event):
        if self.errorFound:
            print 'error'
            return
        if not self.resultQ.empty():
            print 'match found!'
            thread.start_new(sendEmail, (self.emailAddr,))
            _ = self.resultQ.get()
            self.errorFound = True
            self.mainWindow.lblError.SetBackgroundColour((255,0,0))
            self.mainWindow.Refresh()
            self.mainWindow.timerScreenshot.Stop()
            self.stop(event)
            self.errorFound = False
            return
        print 'no match found'
        thread.start_new(takeScreenshot, (self.resultQ, self.matchImage))


def takeScreenshot(Queue=None, matchImage=None):
    screenshot = ImageGrab.grab()
    screenshot.save(TEMPFILENAME)
    screenImage = cv2.imread(TEMPFILENAME)

    result = cv2.matchTemplate(screenImage, matchImage, cv2.TM_SQDIFF_NORMED)
    mn, _, mnLoc, _ = cv2.minMaxLoc(result)
    if mn < THRESHOLD:
        Queue.put('match')

def sendEmail(emailaddr=TOADDR):
    MAILSERVER.sendmail(FROMADDR, emailaddr, MESSAGE % (FROMADDR, emailaddr))


def main():
    app = wx.App()
    controller = Controller()
    controller.show()
    app.MainLoop()


if __name__ == '__main__':
    main()