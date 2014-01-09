from deptx.helpers import random_chars
from deptx import friendly_id
from deptx.settings import STATIC_URL, MEDIA_URL

class Clearance():
    CLEARANCE_BLACK = -1
    CLEARANCE_BLUE = 0
    CLEARANCE_GREEN = 10
    CLEARANCE_YELLOW = 20
    CLEARANCE_ORANGE = 30
    CLEARANCE_RED = 40
    CLEARANCE_UV = 100
    
    CHOICES_CLEARANCE_MOPDOCUMENT = (
        (CLEARANCE_BLUE, "BLUE"),
        (CLEARANCE_GREEN, "GREEN"),
        (CLEARANCE_YELLOW, "YELLOW"),
        (CLEARANCE_ORANGE, "ORANGE"),
        (CLEARANCE_RED, "RED"),
    )
    
    CHOICES_CLEARANCE_CRONDOCUMENT = (
        (CLEARANCE_UV, "ULTRAVIOLET"),
    )
    
    
    CHOICES_CLEARANCE_ALL = CHOICES_CLEARANCE_MOPDOCUMENT + CHOICES_CLEARANCE_CRONDOCUMENT + ((CLEARANCE_BLACK, "BLACK"),)
    
    def __init__(self, clearance):
        self.clearance = clearance
    
    def getTrustRequested(self):
        if self.clearance == self.CLEARANCE_BLUE:
            return 0
        elif self.clearance == self.CLEARANCE_GREEN:
            return -10
        elif self.clearance == self.CLEARANCE_YELLOW:
            return -20
        elif self.clearance == self.CLEARANCE_ORANGE:
            return -30
        elif self.clearance == self.CLEARANCE_RED:
            return -40
        elif self.clearance == self.CLEARANCE_UV:
            return -50
    
    def getTrustReportedCorrect(self):
        if self.clearance == self.CLEARANCE_BLUE:
            return 10
        elif self.clearance == self.CLEARANCE_GREEN:
            return 30
        elif self.clearance == self.CLEARANCE_YELLOW:
            return 50
        elif self.clearance == self.CLEARANCE_ORANGE:
            return 70
        elif self.clearance == self.CLEARANCE_RED:
            return 90
        elif self.clearance == self.CLEARANCE_UV:
            return 110
    
    def getTrustReportedIncorrect(self):
        if self.clearance == self.CLEARANCE_BLUE:
            return -5
        elif self.clearance == self.CLEARANCE_GREEN:
            return -15
        elif self.clearance == self.CLEARANCE_YELLOW:
            return -25
        elif self.clearance == self.CLEARANCE_ORANGE:
            return -35
        elif self.clearance == self.CLEARANCE_RED:
            return -45
        elif self.clearance == self.CLEARANCE_UV:
            return -55
    
    def getTrustRevoked(self):
        if self.clearance == self.CLEARANCE_BLUE:
            return -5
        elif self.clearance == self.CLEARANCE_GREEN:
            return -15
        elif self.clearance == self.CLEARANCE_YELLOW:
            return -25
        elif self.clearance == self.CLEARANCE_ORANGE:
            return -35
        elif self.clearance == self.CLEARANCE_RED:
            return -45
        elif self.clearance == self.CLEARANCE_UV:
            return -55
    
    def generateSerial(self, document):
        if self.clearance == self.CLEARANCE_BLUE:
            beginning = "ABCD01"
            end = "MINISTRY"
        elif self.clearance == self.CLEARANCE_GREEN:
            beginning = "EFGH23"
            end = "ORCHID"
        elif self.clearance == self.CLEARANCE_YELLOW:
            beginning = "IJKL45"
            end = "PROVENANCE"
        elif self.clearance == self.CLEARANCE_ORANGE:
            beginning = "MNOP67"
            end = "NOTTINGHAM"
        elif self.clearance == self.CLEARANCE_RED:
            beginning = "QRST89"
            end = "MIXEDREALITYLAB"
        elif self.clearance == self.CLEARANCE_UV:
            #IMPORTANT: CronDocuments are based on a different ID-counter, so no MopDocuments should ever be UV (and all CronDocuments need to be UV)
            beginning = "UVWXYZ"
            end = "URBANANGEL"
        return "DOC-%s-%s-%s%s-%s" % (document.unit.serial, random_chars(size=2, chars=beginning), random_chars(size=1, chars=end), friendly_id.encode(document.id), random_chars(size=4, chars=end))
    
    
    def getBadgeUrl(self):
        path = MEDIA_URL + 'orchid-badge/'
        img = ""
        if self.clearance == Clearance.CLEARANCE_BLUE:
            img = "orchid-blue.png"
        elif self.clearance == Clearance.CLEARANCE_GREEN:
            img = "orchid-green.png"
        elif self.clearance == Clearance.CLEARANCE_YELLOW:
            img = "orchid-yellow.png"
        elif self.clearance == Clearance.CLEARANCE_ORANGE:
            img = "orchid-orange.png"
        elif self.clearance == Clearance.CLEARANCE_RED:
            img = "orchid-red.png"
        elif self.clearance == Clearance.CLEARANCE_UV:
            img = "orchid-ultraviolet.png"
        return path + img

    def getBadgeUrlStar(self):
        path = MEDIA_URL + 'orchid-badge/'
        img = ""
        if self.clearance == Clearance.CLEARANCE_BLACK:
            img = "performance-black.png"
        elif self.clearance == Clearance.CLEARANCE_BLUE:
            img = "performance-blue.png"
        elif self.clearance == Clearance.CLEARANCE_GREEN:
            img = "performance-green.png"
        elif self.clearance == Clearance.CLEARANCE_YELLOW:
            img = "performance-yellow.png"
        elif self.clearance == Clearance.CLEARANCE_ORANGE:
            img = "performance-orange.png"
        elif self.clearance == Clearance.CLEARANCE_RED:
            img = "performance-red.png"
        elif self.clearance == Clearance.CLEARANCE_UV:
            img = "performance-ultraviolet.png"
        return path + img
 
    def getCssUrl(self):
        path = STATIC_URL + 'mop/'
        css = ""
        if self.clearance == self.CLEARANCE_BLUE:
            css = "mop_color_blue.css"
        elif self.clearance == self.CLEARANCE_GREEN:
            css = "mop_color_green.css"
        elif self.clearance == self.CLEARANCE_YELLOW:
            css = "mop_color_yellow.css"
        elif self.clearance == self.CLEARANCE_ORANGE:
            css = "mop_color_orange.css"
        elif self.clearance == self.CLEARANCE_RED:
            css = "mop_color_red.css"
        elif self.clearance == self.CLEARANCE_UV:
            css = "mop_color_ultraviolet.css"
        return path + css

    def getMailUrl(self):
        path = STATIC_URL + 'mop/'
        img = ""
        if self.clearance == self.CLEARANCE_BLUE:
            img = "mail_blue.png"
        elif self.clearance == self.CLEARANCE_GREEN:
            img = "mail_green.png"
        elif self.clearance == self.CLEARANCE_YELLOW:
            img = "mail_yellow.png"
        elif self.clearance == self.CLEARANCE_ORANGE:
            img = "mail_orange.png"
        elif self.clearance == self.CLEARANCE_RED:
            img = "mail_red.png"
        elif self.clearance == self.CLEARANCE_UV:
            img = "mail_ultraviolet.png"
        return path + img
    
def convertTrustIntoClearance(trust, days):
    if trust <= 0:
        return Clearance.CLEARANCE_BLACK
    elif trust < getMinimumGreen(days):
        return Clearance.CLEARANCE_BLUE
    elif trust < getMinimumYellow(days):
        return Clearance.CLEARANCE_GREEN
    elif trust < getMinimumOrange(days):
        return Clearance.CLEARANCE_YELLOW
    elif trust < getMinimumRed(days):
        return Clearance.CLEARANCE_ORANGE
    else:
        return Clearance.CLEARANCE_RED    

def getMinimumGreen(days):
    return 5 * days

def getMinimumYellow(days):
    return 20 * days

def getMinimumOrange(days):
    return 45 * days

def getMinimumRed(days):
    return 80 * days    
    
        
