from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List


def main_menu_keyboard(is_atelier: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    if not is_atelier:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text="🖨 Печать", callback_data="print")]
        )
    return kb


def artworks_keyboard(artworks: List[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for a in artworks:
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=a["artwork_name"],
                    callback_data=f"art_{a['id']}",
                )
            ]
        )
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ])
    return kb


def papers_keyboard(papers: List[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for p in papers:
        label = f"{p['paper_name']} ({p['quantity']})"
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=label, callback_data=f"paper_{p['id']}",
                )
            ]
        )
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Назад", callback_data="back_to_artworks"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel"),
    ])
    return kb


def confirm_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    kb.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", callback_data="confirm_order"
            ),
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        ]
    )
    return kb
