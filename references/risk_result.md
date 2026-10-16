import { loadProfile, loadTxnSelection } from "../../utils/storage";
import { assessRiskFromMockDataset } from "../../utils/riskEngine";

Page({
  data: {
    result: {
      score: 0,
      band: "Yellow",
      pillClass: "pill-yellow",
      strAlert: false,
      issues: [],
      flags: [],
      masRefs: []
    }
  },
  onShow() {
    const profile = loadProfile();
    const sel = loadTxnSelection();
    const result = assessRiskFromMockDataset(profile, sel.rowIndices || [], sel.metaByRowIndex || {});
    this.setData({ result });
  },
  goTransaction() {
    wx.navigateBack();
  }
});

