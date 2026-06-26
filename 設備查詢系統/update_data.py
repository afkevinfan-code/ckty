"""從原始 Excel 更新本機查詢系統的資料檔。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import openpyxl


SOURCE = Path("/Users/kevinfan/Desktop/桃園電池版設備明細表_系統.xlsx")
OUTPUT = Path(__file__).with_name("data.js")


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def marked(value: object) -> bool:
    return text(value).upper().replace("Ｖ", "V") == "V"


def equipment_types(row: tuple[object, ...]) -> list[str]:
    """依總表 V:AE 欄位轉換為使用者可查詢的設備類別。"""
    types: list[str] = []
    # Excel 欄位位置：V=21、W=22、X=23、Y=24、AA=26、AB=27、AD=29、AE=30（0-based）
    if marked(row[21]):
        types.append("市電版自然排水")
    if marked(row[22]):
        types.append("市電版電動排水")
    if marked(row[23]):
        degree = text(row[24])
        types.append(f"路緣石電池版（左{f'／{degree}度' if degree else ''}）")
    if marked(row[26]):
        degree = text(row[27])
        types.append(f"路緣石電池版（右{f'／{degree}度' if degree else ''}）")
    if marked(row[29]):
        types.append("電池版自然排水")
    if marked(row[30]):
        types.append("電池版電動排水")
    return types


def main() -> None:
    workbook = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    sheet = workbook["總表"]
    records: list[dict[str, object]] = []
    seen: set[str] = set()

    for source_row, row in enumerate(sheet.iter_rows(min_row=6, values_only=True), start=6):
        if not row[5]:
            continue
        record = {
            "roadCode": text(row[5]),
            "roadName": text(row[3]),
            "district": text(row[4]),
            "spaceNo": text(row[8]),
            "types": equipment_types(row),
            "deviceCabinetNo": text(row[6]),
            "frontPlateSerial": text(row[31]),
            "rearPlateSerial": text(row[32]),
            "frontSimSn": text(row[33]),
            "rearSimSn": text(row[34]),
            "publicIp": text(row[36]),
            "frontPort": text(row[37]),
            "rearPort": text(row[38]),
            "sourceRow": source_row,
        }
        # 原表有完全相同的重複列，查詢時只保留一筆，避免結果重覆。
        fingerprint = json.dumps(
            {key: value for key, value in record.items() if key != "sourceRow"},
            ensure_ascii=False,
            sort_keys=True,
        )
        if fingerprint not in seen:
            seen.add(fingerprint)
            records.append(record)

    payload = {
        "source": SOURCE.name,
        "updated": date.today().isoformat(),
        "recordCount": len(records),
        "records": records,
    }
    OUTPUT.write_text(
        "window.PARKING_EQUIPMENT_DATA = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"已寫入 {OUTPUT}：{len(records)} 筆去重後資料")


if __name__ == "__main__":
    main()
