import os, ROOT
import cmsstyle as CMS

CMS.SetExtraText("Simulation Preliminary")


class Plotter:
    def __init__(self):
        self.outputPath = "./pdfs"
        os.makedirs(self.outputPath, exist_ok=True)
        self.CreateHistograms()

    def CreateHistograms(self):
        self.data = ROOT.TH1F("data", "data", 50, 0, 100)
        self.bkg = ROOT.TH1F("bkg", "bkg", 50, 0, 100)
        self.signal = ROOT.TH1F("signal", "signal", 50, 0, 100)

        f_exp = ROOT.TF1("exp30","1./30*exp(-1./30)", 0, 100)
        f_gaus305 = ROOT.TF1("gaus305","gaus", 0, 100)
        f_gaus305.SetParameters(1, 30, 5)
        
        self.bkg.FillRandom("exp30", 10000)
        self.data.FillRandom("exp30", 10000)
        self.signal.FillRandom("gaus305", 1000)
        self.data.FillRandom("gaus305", 1000)
        self.signal.Scale(0.1 / self.signal.Integral())
        self.bkg.Scale(1.0 / self.bkg.Integral())
        self.bkg_tot = self.bkg.Clone("bkg_tot")
        self.bkg_tot.Add(self.signal)

        self.data.Scale(self.bkg_tot.Integral() / self.data.Integral())
        self.ratio = self.data.Clone("ratio")
        self.ratio_nosignal = self.data.Clone("ratio_nosignal")

        self.ratio.Divide(self.bkg_tot)
        self.ratio_nosignal.Divide(self.bkg)

        f_gaus2 = ROOT.TF2("gaus2", "xygaus", 0, 5, 0, 5)
        f_gaus2.SetParameters(1, 2.5, 1, 2.5, 1)

        self.hist2d = ROOT.TH2F("hist2d", "2D Histogram", 25, 0, 5, 25, 0, 5)
        self.hist2d.FillRandom("gaus2", 200000)
        self.hist2d.Scale(10.0 / self.hist2d.Integral())

    def Plot(self, square, iPos):
        canv_name = f'example_{"square" if square else "rectangle"}_pos{iPos}'
        CMS.SetLumi("138")
        CMS.SetEnergy("13")
        # Write extra lines below the extra text (usuful to define regions/channels)
        CMS.ResetAdditionalInfo()
        CMS.AppendAdditionalInfo("Signal region")
        CMS.AppendAdditionalInfo("#mu-channel")

        canv = CMS.cmsCanvas(
            canv_name,
            0,
            90,
            1e-3,
            2,
            "X",
            "A.U.",
            square=square,
            extraSpace=0.01,
            iPos=iPos,
        )
        canv.SetLogy(True)
        leg = CMS.cmsLeg(0.60, 0.89 - 0.04 * 4, 0.89, 0.89, textSize=0.04)

        # Draw objects in one line
        stack = ROOT.THStack("stack", "Stacked")
        leg.AddEntry(self.data, "Data", "lp")
        CMS.cmsDrawStack(stack, leg, {"Background": self.bkg, "Signal": self.signal})
        CMS.cmsDraw(self.data, "P", mcolor=ROOT.kBlack)


        # Takes care of fixing overlay and closing object
        CMS.SaveCanvas(canv, os.path.join(self.outputPath, canv_name + ".pdf"))

        canv_name += "_ratio"
        dicanv = CMS.cmsDiCanvas(
            canv_name,
            10,
            90,
            0,
            0.2,
            0.0,
            2.0,
            "X",
            "A.U.",
            "Data/Pred.",
            square=square,
            extraSpace=0.1,
            iPos=iPos,
        )
        dicanv.cd(1)

        leg = CMS.cmsLeg(0.60, 0.89 - 0.05 * 5, 0.89, 0.89, textSize=0.05)
        leg.AddEntry(self.data, "Data", "lp")

        CMS.cmsHeader(leg, "With title", textSize=0.05)

        stack = ROOT.THStack("stack", "Stacked")
        CMS.cmsDrawStack(stack, leg, {"Background": self.bkg, "Signal": self.signal})
        CMS.cmsDraw(self.data, "P", mcolor=ROOT.kBlack)

        CMS.fixOverlay()

        dicanv.cd(2)
        leg_ratio = CMS.cmsLeg(
            0.67, 0.97 - 0.05 * 5, 0.85, 0.97, textSize=0.05, columns=2
        )
        # how alternative way to pass style options
        style = {"style": "hist", "lcolor": ROOT.kAzure + 2, "lwidth": 2, "fstyle": 0}
        CMS.cmsDraw(self.ratio_nosignal, **style)
        CMS.cmsDraw(self.ratio, "P", mcolor=ROOT.kBlack)

        leg_ratio.AddEntry(self.ratio, "Bkg", "lp")
        leg_ratio.AddEntry(self.ratio_nosignal, "Bkg+Signal", "l")

        ref_line = ROOT.TLine(10, 1, 90, 1)
        CMS.cmsDrawLine(ref_line, lcolor=ROOT.kBlack, lstyle=ROOT.kDotted)

        CMS.SaveCanvas(dicanv, os.path.join(self.outputPath, canv_name + ".pdf"))

    def Plot2D(self, square, iPos):
        canv_name = f'example_2D_{"square" if square else "rectangle"}_pos{iPos}'
        # Allow to reduce the size of the lumi info
        scaleLumi = 0.80 if square else None
        canv = CMS.cmsCanvas(
            canv_name,
            0,
            5,
            0,
            5,
            "X",
            "Y",
            square=square,
            extraSpace=0.01,
            iPos=iPos,
            with_z_axis=True,
            scaleLumi=scaleLumi,
        )

        self.hist2d.GetZaxis().SetTitle("Events normalised")
        self.hist2d.GetZaxis().SetTitleOffset(1.4 if square else 1.2)
        self.hist2d.Draw("same colz")
        # Set a new palette
        CMS.SetAlternative2DColor(self.hist2d, CMS.cmsStyle)

        # Allow to adjust palette position
        CMS.UpdatePalettePosition(self.hist2d, canv)

        CMS.SaveCanvas(canv, os.path.join(self.outputPath, canv_name + ".pdf"))

def main():
    plotter = Plotter()
    plotter.Plot(square=CMS.kSquare, iPos=0)
    plotter.Plot(square=CMS.kRectangular, iPos=0)
    plotter.Plot(square=CMS.kSquare, iPos=11)
    plotter.Plot(square=CMS.kRectangular, iPos=11)
    plotter.Plot2D(square=CMS.kSquare, iPos=0)
    plotter.Plot2D(square=CMS.kRectangular, iPos=0)


if __name__ == "__main__":
    main()
