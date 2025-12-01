import db
# from flask_telebot import bot

def record_debt(bot, message, creditor: str, debtor: str, amount: int, msg_id: int):
    with db.get_session() as session:
    # ensure users exist
        for u in {creditor, debtor}:
            if session.get(db.TgUser, u) is None:
                session.add(db.TgUser(username=u))

        # idempotency — ignore repeat of same Telegram message
        # exists = session.exec(
        #     session.query(DebtLedger).filter_by(message_id=msg_id)
        # ).first()
        # if exists:
        #     bot.reply_to(message, "Already recorded.")
        #     return

        # insert ledger row
        # entry = DebtLedger(
        #     creditor=creditor,
        #     debtor=debtor,
        #     amount_din=amount,
        #     message_id=msg_id
        # )
        # session.add(entry)
        # session.commit()




