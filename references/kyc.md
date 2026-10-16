import { loadProfile, saveProfile } from "../../utils/storage";

function ensureBusiness(profile) {
  const b = profile.business || {};
  return {
    ...profile,
    business: {
      uen: b.uen || profile.idNumber || "",
      industry: b.industry || "",
      uboName: b.uboName || "",
      uboId: b.uboId || ""
    }
  };
}

Page({
  data: {
    userTypeOptions: [
      { id: "individual", label: "Individual" },
      { id: "business", label: "Business" }
    ],
    idTypeOptions: [
      { id: "NRIC", label: "NRIC" },
      { id: "Passport", label: "Passport" },
      { id: "UEN", label: "UEN" }
    ],
    userTypeIndex: 0,
    idTypeIndex: 0,
    userType: "individual",
    profile: {
      userType: "individual",
      fullName: "",
      idType: "NRIC",
      idNumber: "",
      nationality: "SG",
      address: "",
      occupation: "",
      sourceOfFunds: "",
      pep: false,
      uboProvided: true,
      business: { uen: "", industry: "", uboName: "", uboId: "" }
    }
  },
  onShow() {
    const saved = loadProfile();
    if (saved) {
      const profile = ensureBusiness(saved);
      const userTypeIndex = this.data.userTypeOptions.findIndex(x => x.id === profile.userType);
      const idTypeIndex = this.data.idTypeOptions.findIndex(x => x.id === profile.idType);
      this.setData({
        profile,
        userType: profile.userType,
        userTypeIndex: userTypeIndex >= 0 ? userTypeIndex : 0,
        idTypeIndex: idTypeIndex >= 0 ? idTypeIndex : 0
      });
    }
    this.refreshIdTypeOptions();
  },
  refreshIdTypeOptions() {
    const userType = this.data.userType;
    let idTypeOptions;
    if (userType === "business") {
      idTypeOptions = [{ id: "UEN", label: "UEN" }];
      this.setData({ idTypeOptions, idTypeIndex: 0 });
      this.setData({ profile: { ...this.data.profile, idType: "UEN" } });
    } else {
      idTypeOptions = [
        { id: "NRIC", label: "NRIC" },
        { id: "Passport", label: "Passport" }
      ];
      const current = this.data.profile.idType;
      const idTypeIndex = idTypeOptions.findIndex(x => x.id === current);
      this.setData({ idTypeOptions, idTypeIndex: idTypeIndex >= 0 ? idTypeIndex : 0 });
      const idType = idTypeOptions[(idTypeIndex >= 0 ? idTypeIndex : 0)].id;
      this.setData({ profile: { ...this.data.profile, idType } });
    }
  },
  onUserTypeChange(e) {
    const idx = Number(e.detail.value || 0);
    const userType = this.data.userTypeOptions[idx].id;
    const profile = ensureBusiness({ ...this.data.profile, userType });
    if (userType === "business") {
      profile.uboProvided = !!profile.uboProvided;
      profile.idType = "UEN";
    }
    this.setData({ userTypeIndex: idx, userType, profile });
    this.refreshIdTypeOptions();
  },
  onIdTypeChange(e) {
    const idx = Number(e.detail.value || 0);
    const idType = this.data.idTypeOptions[idx].id;
    this.setData({ idTypeIndex: idx, profile: { ...this.data.profile, idType } });
  },
  onInput(e) {
    const key = e.currentTarget.dataset.key;
    const value = e.detail.value;
    const next = { ...this.data.profile, [key]: value };
    if (this.data.userType === "business") {
      next.business = { ...(next.business || {}), uen: next.idNumber };
    }
    this.setData({ profile: ensureBusiness(next) });
  },
  onBizInput(e) {
    const key = e.currentTarget.dataset.key;
    const value = e.detail.value;
    const business = { ...this.data.profile.business, [key]: value };
    this.setData({ profile: ensureBusiness({ ...this.data.profile, business }) });
  },
  onTogglePep(e) {
    this.setData({ profile: { ...this.data.profile, pep: !!e.detail.value } });
  },
  onToggleUboProvided(e) {
    const v = !!e.detail.value;
    let business = { ...this.data.profile.business };
    if (!v) business = { ...business, uboName: "", uboId: "" };
    this.setData({ profile: ensureBusiness({ ...this.data.profile, uboProvided: v, business }) });
  },
  onSave() {
    const profile = ensureBusiness(this.data.profile);
    saveProfile(profile);
    wx.showToast({ title: "Saved", icon: "success" });
  },
  goTxns() {
    this.onSave();
    wx.navigateTo({ url: "/pages/transaction/transaction" });
  }
});

