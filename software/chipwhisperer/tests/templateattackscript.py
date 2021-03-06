# Date Auto-Generated: 2016.06.09-16.47.02
from chipwhisperer.common.scripts.base import UserScriptBase
# Imports from Preprocessing
import chipwhisperer.analyzer.preprocessing as preprocessing
# Imports from Attack
from chipwhisperer.analyzer.attacks.profiling import Profiling
from chipwhisperer.analyzer.attacks.profiling_algorithms.template import ProfilingTemplate
from chipwhisperer.analyzer.utils.Partition import PartitionHWIntermediate
# Imports from utilList
from chipwhisperer.analyzer.utils.TraceExplorerScripts.PartitionDisplay import DifferenceModeTTest, DifferenceModeSAD
from chipwhisperer.analyzer.ui.CWAnalyzerGUI import CWAnalyzerGUI

class Capture(UserScriptBase):
    _name = "Template Attack Script"
    _description = "Template Attack Script"

    def run(self):
        #User commands here
        self.api.setParameter(['Generic Settings', 'Scope Module', 'ChipWhisperer/OpenADC'])
        self.api.setParameter(['Generic Settings', 'Target Module', 'Simple Serial'])
        self.api.setParameter(['Generic Settings', 'Trace Format', 'ChipWhisperer/Native'])
        self.api.setParameter(['Simple Serial', 'Connection', 'ChipWhisperer-Lite'])
        self.api.setParameter(['ChipWhisperer/OpenADC', 'Connection', 'ChipWhisperer-Lite'])

        self.api.connect()

        #Example of using a list to set parameters. Slightly easier to copy/paste in this format
        lstexample = [['CW Extra Settings', 'Trigger Pins', 'Target IO4 (Trigger Line)', True],
                      ['CW Extra Settings', 'Target IOn Pins', 'Target IO1', 'Serial RXD'],
                      ['CW Extra Settings', 'Target IOn Pins', 'Target IO2', 'Serial TXD'],
                      ['OpenADC', 'Clock Setup', 'CLKGEN Settings', 'Desired Frequency', 7370000.0],
                      ['CW Extra Settings', 'Target HS IO-Out', 'CLKGEN'],
                      ['OpenADC', 'Clock Setup', 'ADC Clock', 'Source', 'CLKGEN x4 via DCM'],
                      ['OpenADC', 'Trigger Setup', 'Total Samples', 3000],
                      ['OpenADC', 'Trigger Setup', 'Offset', 1250],
                      ['OpenADC', 'Gain Setting', 'Setting', 45],
                      ['OpenADC', 'Trigger Setup', 'Mode', 'rising edge'],
                      #Final step: make DCMs relock in case they are lost
                      ['OpenADC', 'Clock Setup', 'ADC Clock', 'Reset ADC DCM', None],
                      ]

        #Download all hardware setup parameters
        for cmd in lstexample: self.api.setParameter(cmd)

        #Let's only do a few traces
        self.api.setParameter(['Generic Settings', 'Acquisition Settings', 'Number of Traces', 50])

        #Capture a set of traces and save the project
        self.api.setParameter(['Generic Settings', 'Basic', 'Key', 'Random'])
        self.api.setParameter(['Generic Settings', 'Acquisition Settings', 'Number of Traces', 1500])
        self.api.saveProject("../../projects/tut_randkey_randplain.cwp")
        self.api.captureM()
        self.api.saveProject()
        self.api.newProject()
        self.api.saveProject("../../projects/tut_fixedkey_randplain.cwp")
        self.api.setParameter(['Generic Settings', 'Basic', 'Key', 'Fixed'])
        self.api.setParameter(['Generic Settings', 'Acquisition Settings', 'Number of Traces', 20])
        self.api.captureM()
        self.api.saveProject()


class Attack(UserScriptBase):
    _name = "Template Attack Script"
    _description = "Template Attack Script"

    def initAnalysis(self):
        self.attack = Profiling()
        self.attack.setProject(self.api.project())
        self.attack.setTraceSource(self.traces)
        self.attack.setAnalysisAlgorithm(ProfilingTemplate)
        self.attack.setTraceStart(0)
        self.attack.setTracesPerAttack(1500)
        self.attack.setIterations(1)
        self.attack.setReportingInterval(10)
        self.attack.setTargetBytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.attack.setPointRange((0,2999))

    def initAnalysis2(self):
        self.attack = Profiling()
        self.attack.setProject(self.api.project())
        self.attack.setTraceSource(self.traces)
        self.attack.setAnalysisAlgorithm(ProfilingTemplate)
        self.attack.setTraceStart(0)
        self.attack.setTracesPerAttack(20)
        self.attack.setIterations(1)
        self.attack.setReportingInterval(1)
        self.attack.setTargetBytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.attack.setPointRange((0,2999))

    def initReporting(self):
        # Configures the attack observers (usually a set of GUI widgets)
        self.api.getResults("Attack Settings").setAnalysisSource(self.attack)
        self.api.getResults("Correlation vs Traces in Attack").setAnalysisSource(self.attack)
        self.api.getResults("Output vs Point Plot").setAnalysisSource(self.attack)
        self.api.getResults("PGE vs Trace Plot").setAnalysisSource(self.attack)
        self.api.getResults("Results Table").setAnalysisSource(self.attack)
        self.api.getResults("Save to Files").setAnalysisSource(self.attack)
        self.api.getResults("Trace Output Plot").setTraceSource(self.traces)
        self.api.getResults("Trace Recorder").setTraceSource(self.traces)

    def run(self):
        self.api.openProject("../../projects/tut_randkey_randplain.cwp")
        self.traces = self.api.project().traceManager()
        self.initAnalysis()
        self.initReporting()
        self.generateTemplates()
        self.api.saveProject()
        template = self.api.project().getDataConfig(sectionName="Template Data", subsectionName="Templates")
        self.api.openProject("../../projects/tut_fixedkey_randplain.cwp")
        self.api.project().addDataConfig(template[-1], sectionName="Template Data", subsectionName="Templates")
        self.traces = self.api.project().traceManager()
        self.initAnalysis2()
        self.initReporting()
        self.attack.processTraces()

    def TraceExplorerDialog_PartitionDisplay_displayPartitionStats(self):
        self.cwagui = CWAnalyzerGUI.getInstance()
        ted = self.cwagui.attackScriptGen.utilList[0].exampleScripts[0]
        ted.setTraceSource(self.traces)
        progressBar = ted.parent.getProgressIndicator()
        ted.partObject.setPartMethod(PartitionHWIntermediate)
        partData = ted.partObject.generatePartitions(saveFile=True, loadFile=False)
        partStats = ted.generatePartitionStats(partitionData={"partclass":PartitionHWIntermediate, "partdata":partData}, saveFile=True, progressBar=progressBar)
        partDiffs = ted.generatePartitionDiffs(DifferenceModeSAD, statsInfo={"partclass":PartitionHWIntermediate, "stats":partStats}, saveFile=True, loadFile=False, progressBar=progressBar)
        ted.displayPartitions(differences={"partclass":PartitionHWIntermediate, "diffs":partDiffs})
        ted.poi.setDifferences(partDiffs)

    def TraceExplorerDialog_PartitionDisplay_findPOI(self):
        self.cwagui = CWAnalyzerGUI.getInstance()
        ted = self.cwagui.attackScriptGen.utilList[0].exampleScripts[0]
        return ted.poi.calcPOI(numMax=3, pointRange=(0, 3000), minSpace=5)['poi']

    def generateTemplates(self):
        self.TraceExplorerDialog_PartitionDisplay_displayPartitionStats()
        tRange = (0, 1499)
        poiList = self.TraceExplorerDialog_PartitionDisplay_findPOI()
        partMethod = PartitionHWIntermediate()
        templatedata = self.attack.attack.profiling.generate(tRange, poiList, partMethod)
        tfname = self.attack.attack.saveTemplatesToProject(tRange, templatedata)

if __name__ == '__main__':
    import sys
    from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI
    import chipwhisperer.analyzer.ui.CWAnalyzerGUI as cwa
    from chipwhisperer.common.utils.parameter import Parameter
    app = cwa.makeApplication()     # Comment if you don't need the GUI
    Parameter.usePyQtGraph = True   # Comment if you don't need the GUI
    api = CWCoreAPI()               # Instantiate the API
    api.runScriptClass(Capture)
    gui = cwa.CWAnalyzerGUI(api)    # Comment if you don't need the GUI
    gui.show()                      # Comment if you don't need the GUI
    api.runScriptClass(Attack)

    sys.exit(app.exec_())           # Comment if you don't need the GUI