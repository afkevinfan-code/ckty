const data = window.PARKING_EQUIPMENT_DATA;
const form = document.querySelector("#search-form");
const roadCodeInput = document.querySelector("#road-code");
const spaceNoInput = document.querySelector("#space-no");
const typeInput = document.querySelector("#equipment-type");
const message = document.querySelector("#form-message");
const resultsSection = document.querySelector("#results-section");
const resultList = document.querySelector("#result-list");
const resultSummary = document.querySelector("#result-summary");
const copyButton = document.querySelector("#copy-button");

document.querySelector("#data-status").textContent = `資料來源：${data.source}｜${data.recordCount} 筆`;

function normalize(value) { return String(value || "").trim().replace(/\s/g, ""); }
function normalizeSpace(value) { const cleaned = normalize(value); return /^\d+$/.test(cleaned) ? String(Number(cleaned)) : cleaned.toUpperCase(); }
function sameSpace(left, right) { return normalizeSpace(left) === normalizeSpace(right); }
function display(value) { return value || "—"; }
function matchesType(record, filter) { return !filter || record.types.some((type) => type.includes(filter)); }

function render(records, roadCode) {
  resultsSection.hidden = false;
  resultList.replaceChildren();
  resultSummary.textContent = `路段代碼 ${roadCode}：共找到 ${records.length} 筆資料。`;
  copyButton.hidden = records.length === 0;
  if (!records.length) {
    resultList.innerHTML = '<div class="empty">查無符合資料。請確認路段代碼、車格編號或設備類別。</div>';
    return;
  }
  const template = document.querySelector("#result-template");
  records.forEach((record) => {
    const fragment = template.content.cloneNode(true);
    fragment.querySelector(".result-location").textContent = `${display(record.district)}｜${display(record.roadName)}｜路段代碼 ${record.roadCode}`;
    fragment.querySelector("h3").textContent = `車格編號：${display(record.spaceNo)}`;
    const badges = fragment.querySelector(".badges");
    (record.types.length ? record.types : ["未標示設備類別"]).forEach((type) => { const tag = document.createElement("span"); tag.className = "badge"; tag.textContent = type; badges.append(tag); });
    const fields = [
      ["設備類別", record.types.join("、")], ["電池式編號／控制櫃編號", record.deviceCabinetNo],
      ["前車牌序號", record.frontPlateSerial], ["後車牌序號", record.rearPlateSerial],
      ["前車牌 SIM SN.", record.frontSimSn], ["後車牌 SIM SN.", record.rearSimSn],
      ["市電版對外 IP", record.publicIp], ["前車牌對外 PORT.", record.frontPort], ["後車牌對外 PORT.", record.rearPort],
    ];
    const detailGrid = fragment.querySelector(".detail-grid");
    fields.forEach(([label, value]) => { const cell = document.createElement("div"); const dt = document.createElement("dt"); const dd = document.createElement("dd"); dt.textContent = label; dd.textContent = display(value); cell.append(dt, dd); detailGrid.append(cell); });
    fragment.querySelector(".source-note").textContent = `來源：${data.source}「總表」第 ${record.sourceRow} 列`;
    resultList.append(fragment);
  });
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const roadCode = normalize(roadCodeInput.value);
  const spaceNo = normalize(spaceNoInput.value);
  const type = typeInput.value;
  if (!roadCode) { message.textContent = "請先輸入路段代碼。"; roadCodeInput.focus(); resultsSection.hidden = true; return; }
  message.textContent = "";
  const records = data.records.filter((record) => normalize(record.roadCode) === roadCode && (!spaceNo || sameSpace(record.spaceNo, spaceNo)) && matchesType(record, type));
  render(records, roadCode);
});

document.querySelector("#reset-button").addEventListener("click", () => { form.reset(); message.textContent = ""; resultsSection.hidden = true; roadCodeInput.focus(); });
copyButton.addEventListener("click", async () => { const text = resultList.innerText; try { await navigator.clipboard.writeText(text); copyButton.textContent = "已複製"; setTimeout(() => { copyButton.textContent = "複製結果"; }, 1400); } catch { message.textContent = "瀏覽器未允許自動複製，請直接選取結果文字。"; } });
