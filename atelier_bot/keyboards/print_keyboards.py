from typing import List

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


def main_menu_keyboard(is_atelier: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    if not is_atelier:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text="🖨 Печать", callback_data="print")]
        )
    else:
        kb.inline_keyboard.append([
            InlineKeyboardButton(
                text="➕ Добавить работу", callback_data="add_art"),
            InlineKeyboardButton(
                text="➕ Добавить бумагу", callback_data="add_paper")
        ])
    return kb


def main_reply_keyboard(is_atelier: bool) -> ReplyKeyboardMarkup:
    """Create persistent reply keyboard for main menu."""
    kb = ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        one_time_keyboard=False,
        persistent=True
    )

    if not is_atelier:
        # Keyboard for artists
        kb.keyboard.append([
            KeyboardButton(text="🖨 Печать")
        ])
    else:
        # Keyboard for atelier
        kb.keyboard.append([
            KeyboardButton(text="➕ Добавить работу"),
            KeyboardButton(text="➕ Добавить бумагу")
        ])

    return kb


def artworks_keyboard(artworks: List[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for a in artworks:
        icon_indicator = "🖼️ " if a.get("image_icon") else ""
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{icon_indicator}{a['artwork_name']}",
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


def users_keyboard(users: List[dict]) -> InlineKeyboardMarkup:
    """Create keyboard for selecting a user."""
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for user in users:
        username = user.get("username") or f"user_{user['user_id']}"
        label = f"@{username} (ID: {user['user_id']})"
        kb.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"user_{user['user_id']}",
                )
            ]
        )
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ])
    return kb
