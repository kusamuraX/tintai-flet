from datetime import datetime
import threading
import flet as ft

from tintai_flet.scraping import scraping_tintai_data

timer_thread = None
m_page = None
table = None
update_text = None
data_count_text = None


def get_table_row_data() -> list:
    tintai_data_list = scraping_tintai_data()
    new_count = 0
    table_row_data = []
    for row in tintai_data_list.itertuples():
        title = ft.Text(row.name)
        if row.is_new:
            new_count += 1
            title = ft.Text(
                spans=[
                    ft.TextSpan("新",
                                style=ft.TextStyle(
                                    bgcolor=ft.colors.YELLOW_300,
                                    color=ft.colors.BLACK)),
                    ft.TextSpan(" "),
                    ft.TextSpan(row.name)
                ]
            )
        cell_data = [
            ft.DataCell(title),
            ft.DataCell(ft.Text(row.address)),
            ft.DataCell(ft.Text(row.rent)),
            ft.DataCell(ft.Text(row.admin)),
            ft.DataCell(ft.Text(row.menseki)),
            ft.DataCell(ft.Text(row.floor)),
            ft.DataCell(ft.Text(
                spans=[
                    ft.TextSpan(
                        "詳細",
                        ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                        url=row.link,
                    )
                ]
            )),
        ]
        table_row_data.append(
            ft.DataRow(
                cells=cell_data
            )
        )
        update_text.value = f"情報取得日時：{datetime.now().strftime('%Y/%m/%d %H:%M')}"
        data_count_text.value = f"件数：{len(tintai_data_list)} （新着：{new_count}）"
    return table_row_data


def get_data_timer():
    table.rows = get_table_row_data()
    m_page.update()
    timer_thread = threading.Timer(3600.0, get_data_timer)
    timer_thread.start()


def main(page: ft.Page):
    page.title = "賃貸情報"
    page.window_width = 1100
    page.window_height = 400
    global m_page
    m_page = page

    # データ部
    lv = ft.ListView(height=300, spacing=5, padding=5)

    global table
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("建物名")),
            ft.DataColumn(ft.Text("住所")),
            ft.DataColumn(ft.Text("賃料")),
            ft.DataColumn(ft.Text("管理費")),
            ft.DataColumn(ft.Text("面積")),
            ft.DataColumn(ft.Text("階")),
            ft.DataColumn(ft.Text("リンク")),
        ],
        rows=[],
    )
    lv.controls.append(table)

    data_container = ft.Container(
        content=lv,
        alignment=ft.alignment.center,
        padding=5,
    )

    # 上部
    global update_text
    update_text = ft.Text(value="情報取得日時：")

    global data_count_text
    data_count_text = ft.Text(value="件数：0 （新着：0）")

    def reload_action(e):
        table.rows = []
        page.update()
        table.rows = get_table_row_data()
        page.update()

    reload_btn = ft.FilledButton(text="情報取得", on_click=reload_action)

    top_row = ft.Row(
        [reload_btn, update_text, data_count_text],
    )

    top_container = ft.Container(
        content=top_row,
        alignment=ft.alignment.center,
        padding=3,
    )

    # baseレイアウト
    cols = ft.Column(
        [top_container, data_container],
        alignment=ft.alignment.center,
        horizontal_alignment=ft.alignment.center,
    )

    # baseコンテナ
    container = ft.Container(
        content=cols,
        alignment=ft.alignment.center,
    )
    page.add(container)

    # データ取得スレッド
    global timer_thread
    timer_thread = threading.Timer(1.0, get_data_timer)
    timer_thread.start()

    page.update()


ft.app(target=main)
