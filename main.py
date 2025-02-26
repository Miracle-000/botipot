import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.filters import Command
import math

# Твой токен бота (замени на свой)
TOKEN = "7570400659:AAEE4tWjqHNns_eTZ2qGUcNQb6MGTd_3-kw"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляров бота, диспетчера и роутера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Состояния
class MortgageForm(StatesGroup):
    loan_amount = State()  # Состояние для суммы кредита
    interest_rate = State()  # Состояние для процентной ставки
    loan_term = State()  # Состояние для срока кредита
    down_payment = State()  # Состояние для первоначального взноса

# Функция для расчета ежемесячного платежа по ипотеке
def calculate_mortgage(loan_amount, interest_rate, loan_term):
    monthly_rate = (interest_rate / 100) / 12  # Месячная процентная ставка
    loan_term_months = loan_term * 12  # Срок кредита в месяцах
    if monthly_rate == 0:  # Если ставка 0%, просто делим сумму на срок
        return loan_amount / loan_term_months
    annuity_factor = (monthly_rate * math.pow(1 + monthly_rate, loan_term_months)) / (math.pow(1 + monthly_rate, loan_term_months) - 1)
    return loan_amount * annuity_factor

# Начало работы с ботом, при запуске
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(MortgageForm.loan_amount)  # Начинаем с запроса суммы кредита
    await message.answer("Привет! Я ипотечный калькулятор. Введи сумму кредита (в рублях):")

# Обработка суммы кредита
@router.message(MortgageForm.loan_amount)
async def process_loan_amount(message: Message, state: FSMContext):
    try:
        loan_amount = float(message.text)
        await state.update_data(loan_amount=loan_amount)  # Сохраняем сумму кредита в состоянии
        await state.set_state(MortgageForm.interest_rate)  # Переходим к следующему вопросу
        await message.answer("Теперь введи процентную ставку (%):")
    except ValueError:
        await message.answer("Пожалуйста, введи правильную сумму кредита в рублях.")

# Обработка процентной ставки
@router.message(MortgageForm.interest_rate)
async def process_interest_rate(message: Message, state: FSMContext):
    try:
        interest_rate = float(message.text)
        await state.update_data(interest_rate=interest_rate)  # Сохраняем процентную ставку
        await state.set_state(MortgageForm.loan_term)  # Переходим к следующему вопросу
        await message.answer("Теперь введи срок кредита (в годах):")
    except ValueError:
        await message.answer("Пожалуйста, введи правильную процентную ставку.")

# Обработка срока кредита
@router.message(MortgageForm.loan_term)
async def process_loan_term(message: Message, state: FSMContext):
    try:
        loan_term = int(message.text)
        await state.update_data(loan_term=loan_term)  # Сохраняем срок кредита
        await state.set_state(MortgageForm.down_payment)  # Переходим к следующему вопросу
        await message.answer("Теперь введи первоначальный взнос (в рублях):")
    except ValueError:
        await message.answer("Пожалуйста, введи правильный срок кредита.")

# Обработка первоначального взноса
@router.message(MortgageForm.down_payment)
async def process_down_payment(message: Message, state: FSMContext):
    try:
        down_payment = float(message.text)
        user_data = await state.get_data()
        loan_amount = user_data['loan_amount']
        interest_rate = user_data['interest_rate']
        loan_term = user_data['loan_term']


# Вычитаем первоначальный взнос из суммы кредита
        loan_amount -= down_payment

        # Рассчитываем ежемесячный платеж
        monthly_payment = calculate_mortgage(loan_amount, interest_rate, loan_term)
        await message.answer(f"Ежемесячный платеж: {monthly_payment:,.2f} рублей (с учётом первоначального взноса в {down_payment:,.2f} рублей)")
        
        # Завершаем разговор
        await state.clear()  # Очистка состояния, чтобы начать новый расчет
    except ValueError:
        await message.answer("Пожалуйста, введи правильный первоначальный взнос.")

# Функция для запуска бота
async def main():
    dp.include_router(router)  # Подключаем роутер
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())