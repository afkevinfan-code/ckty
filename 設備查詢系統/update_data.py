"""從原始 Excel 更新本機查詢系統的資料檔。"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import openpyxl


SOURCE = Path("/Users/kevinfan/Desktop/桃園電池版設備明細表系統_v0630.xlsx")
OUTPUT = Path(__file__).with_name("data.js")


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def cell_text(cell: openpyxl.cell.cell.Cell, fallback_digits: int | None = None) -> str:
    """讀取 Excel 顯示格式，保留識別碼的前導零。"""
    value = cell.value
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)) and float(value).is_integer():
        display_format = cell.number_format.split(";")[0].strip()
        zero_format = re.fullmatch(r"0+", display_format)
        if zero_format:
            return f"{int(value):0{len(display_format)}d}"
        if fallback_digits:
            return f"{int(value):0{fallback_digits}d}"
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

    for source_row, cells in enumerate(sheet.iter_rows(min_row=6), start=6):
        row = tuple(cell.value for cell in cells)
        if not row[5]:
            continue
        record = {
            "roadCode": cell_text(cells[5]),
            "roadName": cell_text(cells[3]),
            "district": cell_text(cells[4]),
            "spaceNo": cell_text(cells[8]),
            "types": equipment_types(row),
            "deviceCabinetNo": cell_text(cells[6]),
            "frontPlateSerial": cell_text(cells[31], fallback_digits=12),
            "rearPlateSerial": cell_text(cells[32], fallback_digits=12),
            "frontSimSn": cell_text(cells[33]),
            "rearSimSn": cell_text(cells[34]),
            "publicIp": cell_text(cells[36]),
            "frontPort": cell_text(cells[37]),
            "rearPort": cell_text(cells[38]),
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
