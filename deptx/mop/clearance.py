from deptx.helpers import random_chars
from deptx import friendly_id
from deptx.settings import STATIC_URL, MEDIA_URL

class Clearance():

    CLEARANCE_LOW = 0
    CLEARANCE_GUARDED = 10
    CLEARANCE_ELEVATED = 20
    CLEARANCE_HIGH = 30
    CLEARANCE_SEVERE = 40
    CLEARANCE_MAX = 100
    
    CHOICES_CLEARANCE_MOPDOCUMENT = (
        (CLEARANCE_LOW, "BLUE"),
        (CLEARANCE_GUARDED, "GREEN"),
        (CLEARANCE_ELEVATED, "YELLOW"),
        (CLEARANCE_HIGH, "ORANGE"),
        (CLEARANCE_SEVERE, "RED"),
    )
    
    CHOICES_CLEARANCE_CRONDOCUMENT = (
        (CLEARANCE_MAX, "ULTRAVIOLET"),
    )
    
    CHOICES_CLEARANCE_ALL = CHOICES_CLEARANCE_MOPDOCUMENT + CHOICES_CLEARANCE_CRONDOCUMENT
    
    def __init__(self, clearance):
        self.clearance = clearance
    
    def getTrustRequested(self):
        if self.clearance == self.CLEARANCE_LOW:
            return 0
        elif self.clearance == self.CLEARANCE_GUARDED:
            return -10
        elif self.clearance == self.CLEARANCE_ELEVATED:
            return -20
        elif self.clearance == self.CLEARANCE_HIGH:
            return -30
        elif self.clearance == self.CLEARANCE_SEVERE:
            return -40
        elif self.clearance == self.CLEARANCE_MAX:
            return -50
    
    def getTrustReportedCorrect(self):
        if self.clearance == self.CLEARANCE_LOW:
            return 10
        elif self.clearance == self.CLEARANCE_GUARDED:
            return 30
        elif self.clearance == self.CLEARANCE_ELEVATED:
            return 50
        elif self.clearance == self.CLEARANCE_HIGH:
            return 80
        elif self.clearance == self.CLEARANCE_SEVERE:
            return 150
        elif self.clearance == self.CLEARANCE_MAX:
            return 200
    
    def getTrustReportedIncorrect(self):
        if self.clearance == self.CLEARANCE_LOW:
            return -5
        elif self.clearance == self.CLEARANCE_GUARDED:
            return -15
        elif self.clearance == self.CLEARANCE_ELEVATED:
            return -25
        elif self.clearance == self.CLEARANCE_HIGH:
            return -40
        elif self.clearance == self.CLEARANCE_SEVERE:
            return -75
        elif self.clearance == self.CLEARANCE_MAX:
            return -100
    
    def getTrustRevoked(self):
        if self.clearance == self.CLEARANCE_LOW:
            return -5
        elif self.clearance == self.CLEARANCE_GUARDED:
            return -15
        elif self.clearance == self.CLEARANCE_ELEVATED:
            return -25
        elif self.clearance == self.CLEARANCE_HIGH:
            return -40
        elif self.clearance == self.CLEARANCE_SEVERE:
            return -75
        elif self.clearance == self.CLEARANCE_MAX:
            return -100
    
    def generateSerial(self, document):
        if self.clearance == self.CLEARANCE_LOW:
            beginning = "ABCD01"
            end = "MINISTRY"
        elif self.clearance == self.CLEARANCE_GUARDED:
            beginning = "EFGH23"
            end = "ORCHID"
        elif self.clearance == self.CLEARANCE_ELEVATED:
            beginning = "IJKL45"
            end = "PROVENANCE"
        elif self.clearance == self.CLEARANCE_HIGH:
            beginning = "MNOP67"
            end = "NOTTINGHAM"
        elif self.clearance == self.CLEARANCE_SEVERE:
            beginning = "QRST89"
            end = "MIXEDREALITYLAB"
        elif self.clearance == self.CLEARANCE_MAX:
            beginning = "UVWXYZ"
            end = "URBANANGEL"
        return "DOC-%s-%s-%s-%s" % (document.unit.serial, random_chars(size=2, chars=beginning), friendly_id.encode(document.id), random_chars(chars=end))
    
    
    def getBadgeUrl(self):
        path = MEDIA_URL + 'orchid-badge/'
        img = ""
        if self.clearance == Clearance.CLEARANCE_LOW:
            img = "orchid-blue.png"
        elif self.clearance == Clearance.CLEARANCE_GUARDED:
            img = "orchid-green.png"
        elif self.clearance == Clearance.CLEARANCE_ELEVATED:
            img = "orchid-yellow.png"
        elif self.clearance == Clearance.CLEARANCE_HIGH:
            img = "orchid-orange.png"
        elif self.clearance == Clearance.CLEARANCE_SEVERE:
            img = "orchid-red.png"
        elif self.clearance == Clearance.CLEARANCE_MAX:
            img = "orchid-ultraviolet.png"
        return path + img
 
    def getCssUrl(self):
        path = STATIC_URL + 'mop/'
        css = ""
        if self.clearance == self.CLEARANCE_LOW:
            css = "mop_color_blue.css"
        elif self.clearance == self.CLEARANCE_GUARDED:
            css = "mop_color_green.css"
        elif self.clearance == self.CLEARANCE_ELEVATED:
            css = "mop_color_yellow.css"
        elif self.clearance == self.CLEARANCE_HIGH:
            css = "mop_color_orange.css"
        elif self.clearance == self.CLEARANCE_SEVERE:
            css = "mop_color_red.css"
        elif self.clearance == self.CLEARANCE_MAX:
            css = "mop_color_ultraviolet.css"
        return path + css

    def getMailUrl(self):
        path = STATIC_URL + 'mop/'
        img = ""
        if self.clearance == self.CLEARANCE_LOW:
            img = "mail_blue.png"
        elif self.clearance == self.CLEARANCE_GUARDED:
            img = "mail_green.png"
        elif self.clearance == self.CLEARANCE_ELEVATED:
            img = "mail_yellow.png"
        elif self.clearance == self.CLEARANCE_HIGH:
            img = "mail_orange.png"
        elif self.clearance == self.CLEARANCE_SEVERE:
            img = "mail_red.png"
        elif self.clearance == self.CLEARANCE_MAX:
            img = "mail_ultraviolet.png"
        return path + img
    
def convertTrustIntoClearance(trust):
    if trust <= 99:
        return Clearance.CLEARANCE_LOW
    elif trust <=199:
        return Clearance.CLEARANCE_GUARDED
    elif trust <=299:
        return Clearance.CLEARANCE_ELEVATED
    elif trust <=499:
        return Clearance.CLEARANCE_HIGH
    elif trust <=10000000:
        return Clearance.CLEARANCE_SEVERE
    else:
        return Clearance.CLEARANCE_MAX
    
def getAdjustedClearance(clearance, gainedTrust):
    proposedClearance = convertTrustIntoClearance(gainedTrust)
    if proposedClearance >= clearance:
        return proposedClearance
    else:
        if clearance >= Clearance.CLEARANCE_MAX:
            return Clearance.CLEARANCE_SEVERE
        elif clearance == Clearance.CLEARANCE_SEVERE:
            return Clearance.CLEARANCE_HIGH
        elif clearance == Clearance.CLEARANCE_HIGH:
            return Clearance.CLEARANCE_ELEVATED
        elif clearance == Clearance.CLEARANCE_ELEVATED:
            return Clearance.CLEARANCE_GUARDED
        elif clearance == Clearance.CLEARANCE_GUARDED:
            return Clearance.CLEARANCE_LOW
        else:
            return Clearance.CLEARANCE_LOW
    
    
    
    
    
        
