from PIL import ImageGrab, Image
import numpy as np
import cv2
from cv2 import matchTemplate as cv2m
import os
import time
import smtplib
import wx


from view import View


MAILSERVER = smtplib.SMTP('outlook.office365.com', 587)
MAILSERVER.starttls()
MAILSERVER.ehlo()
MAILSERVER.login("info@atumsoft.com", "\"d~XsN*9;+<Ec:ZB")
FROMADDR = 'info@atumsoft.com'
TOADDR = ''
TEMPFILENAME = 'temp.png'
THRESHOLD = .7

MESSAGE = """From: %s
To: %s
Subject: Instrument Error

Software issue detected, your attention required.
"""


class Controller:
    def __init__(self):
        self.mainWindow = View(None)

        self.mainWindow.Bind(wx.EVT_BUTTON, self.start, self.mainWindow.btnStart)
        self.mainWindow.Bind(wx.EVT_BUTTON, self.stop, self.mainWindow.btnStop)
        self.mainWindow.Bind(wx.EVT_CLOSE, self.shutdown)

        self.matchImage = cv2.imread(os.path.normpath('redBox.png'))

    def show(self):
        self.mainWindow.Show()

    def start(self, event):
        self.mainWindow.txtEmail.Disable()

    def stop(self, event):
        self.mainWindow.txtEmail.Enable()

    def shutdown(self, event):
        MAILSERVER.close()

    def takeScreenshot(self, event):
        screenshot = ImageGrab.grab()
        screenshot.save(TEMPFILENAME)

        self.screenImage = cv2.imread(TEMPFILENAME)

    def imgSearch(self):
        result = cv2.matchTemplate(self.screenImage, self.matchImage, cv2.TM_SQDIFF_NORMED)
        mn, _, mnLoc, _ = cv2.minMaxLoc(result)
        if mn < THRESHOLD:
            MAILSERVER.sendmail(FROMADDR, TOADDR, MESSAGE % (FROMADDR, TOADDR))
            print 'match!'


def main():
    app = wx.App()
    controller = Controller()
    controller.show()
    app.MainLoop()


if __name__ == '__main__':
    main()