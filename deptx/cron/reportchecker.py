from cron.models import CaseQuestionInstance, CaseInstance, HelpMail
from assets.models import CaseQuestion

def analyze_reports():
    questionInstance_list = CaseQuestionInstance.objects.filter(correct=False).filter(submitted=True).exclude(question__questionType=CaseQuestion.TYPE_MULTIPLE_CHOICE).exclude(question__questionType=CaseQuestion.TYPE_OPEN)
    caseInstance_list = []
    for questionInstance in questionInstance_list:
        if questionInstance.isBad:
            questionInstance.isBad = False
            questionInstance.submitted = False
        else:
            questionInstance.correct = True
        questionInstance.save()
        caseInstance_list.append(questionInstance.getCaseInstance())
    caseInstance_list = list(set(caseInstance_list))
    for caseInstance in caseInstance_list:
        # we know that a case that had a bad answer now has an unsubmitted answer
        if caseInstance.allQuestionsSubmitted():
            text = "Thanks to work done by you and additional agents we are now certain what happened. Please proceed and check the outcome of your investigation concerning case '%s' in mission %s."  % (caseInstance.case.name, caseInstance.case.mission.name)
        else:
            text = "Agent! We saw your report for case '%s' in mission %s. We expected more thorough work. Please have a look if you can increase the detail of your report. We are counting on you!" % (caseInstance.case.name, caseInstance.case.mission.name)
        helpMail = HelpMail()
        helpMail.type = HelpMail.TYPE_TO_PLAYER
        helpMail.body = text
        helpMail.cron = caseInstance.cron
        helpMail.isRead = False
        helpMail.save()
    
    
#     caseInstance_list = CaseInstance.objects.all()
#     for caseInstance in caseInstance_list:
#         if caseInstance.hasEssayOrFileQuestions() and caseInstance.allQuestionsSubmitted():
#             if caseInstance.hasBadAnswer():
#                 text = "Agent! We saw your report for case '%s' in mission %s We expected more thorough work. Please have a look if you can increase the detail of your report. We are counting on you!" % (caseInstance.case.name, caseInstance.case.mission.name)
#             else:
#                 text = "Thanks to work done by you and additional agents we are now certain what happened. Please proceed and check the outcome of your investigation concerning case '%s' in mission %s."  % (caseInstance.case.name, caseInstance.case.mission.name)
#             questionInstance_list = CaseQuestionInstance.objects.filter(cron=caseInstance.cron, question__case=caseInstance.case).filter(correct=False).exclude(questionType=CaseQuestion.TYPE_MULTIPLE_CHOICE).exclude(questionType=CaseQuestion.TYPE_OPEN)
#             for questionInstance in questionInstance_list:
#                 if questionInstance.isBad:
#                     questionInstance.isBad = False
#                     questionInstance.submitted = False
#                 else:
#                     questionInstance.correct = True
#                 questionInstance.save()
#             helpMail = HelpMail()
#             helpMail.type = HelpMail.TYPE_TO_PLAYER
#             helpMail.body = text
#             helpMail.cron = caseInstance.cron
#             helpMail.isRead = False
#             helpMail.save()
#                 
            
                    
                
    
    
    
    
