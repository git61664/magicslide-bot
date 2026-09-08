from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import os
import zipfile
from config import ZIP_MAX_FILES, ZIP_MAX_FILE_SIZE_MB, ZIP_MAX_TOTAL_MB, PDF_MAX_FILES

router = Router()

class FileStates(StatesGroup):
    collecting_files = State()

@router.message(F.text == "🗜 ZIP qilish")
async def start_zip(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FileStates.collecting_files)
    await state.update_data(zip_files=[], total_size=0)
    await message.answer(
        "🗜 <b>ZIP QILISH</b>\n\n"
        f"Fayllarni yuboring (eng ko'pi {ZIP_MAX_FILES} ta):\n"
        f"• Maksimal fayl: {ZIP_MAX_FILE_SIZE_MB} MB\n"
        f"• Jami: {ZIP_MAX_TOTAL_MB} MB\n\n"
        f"Tayyor bo'lgach 'ZIP qilish' bosing.",
        parse_mode="HTML"
    )

@router.message(FileStates.collecting_files, F.document)
async def collect_file(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    files = data.get("zip_files", [])
    
    if len(files) >= ZIP_MAX_FILES:
        await message.answer(f"❌ Eng ko'pi {ZIP_MAX_FILES} ta fayl.")
        return
    
    doc = message.document
    file_size_mb = doc.file_size / (1024*1024)
    
    if file_size_mb > ZIP_MAX_FILE_SIZE_MB:
        await message.answer(f"❌ Fayl juda katta ({file_size_mb:.1f} MB)")
        return
    
    total = data.get("total_size", 0) + doc.file_size
    if total / (1024*1024) > ZIP_MAX_TOTAL_MB:
        await message.answer(f"❌ Jami hajm juda katta")
        return
    
    files.append({"file_id": doc.file_id, "name": doc.file_name or "file"})
    await state.update_data(zip_files=files, total_size=total)
    
    await message.answer(f"✅ Fayl qabul qilindi ({len(files)}/{ZIP_MAX_FILES})")

@router.message(FileStates.collecting_files, F.text == "🗜 ZIP qilish")
async def process_zip(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    files = data.get("zip_files", [])
    
    if not files:
        await message.answer("❌ Hech bir fayl qo'shilmadi.")
        return
    
    await message.answer("⏳ ZIP arxiv tayyorlanmoqda...")
    
    try:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "archive.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for f in files:
                file = await bot.get_file(f["file_id"])
                fpath = os.path.join(temp_dir, f["name"])
                await bot.download_file(file.file_path, fpath)
                zf.write(fpath, arcname=f["name"])
                os.remove(fpath)
        
        from aiogram.types import FSInputFile
        await bot.send_document(message.chat.id, FSInputFile(zip_path), caption=f"✅ Archive: {len(files)} fayl")
        os.remove(zip_path)
        os.rmdir(temp_dir)
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)}")
        raise e
    
    await state.clear()

@router.message(F.text == "📄 PDF qilish")
async def start_pdf(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FileStates.collecting_files)
    await state.update_data(pdf_files=[])
    await message.answer(
        f"📄 <b>PDF QILISH</b>\n\n"
        f"Word, PowerPoint, rasmlarni yuboring (eng ko'pi {PDF_MAX_FILES} ta):\n\n"
        f"Tayyor bo'lgach /pdf bosing.",
        parse_mode="HTML"
    )

@router.message(FileStates.collecting_files, F.document | F.photo)
async def collect_pdf_file(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get("pdf_files", [])
    
    if len(files) >= PDF_MAX_FILES:
        await message.answer(f"❌ Eng ko'pi {PDF_MAX_FILES} ta fayl.")
        return
    
    if message.document:
        files.append({"file_id": message.document.file_id, "type": "doc", "name": message.document.file_name})
    elif message.photo:
        files.append({"file_id": message.photo[-1].file_id, "type": "photo", "name": f"photo_{len(files)}.jpg"})
    
    await state.update_data(pdf_files=files)
    await message.answer(f"✅ Fayl qabul qilindi ({len(files)}/{PDF_MAX_FILES})")

@router.message(FileStates.collecting_files, Command("pdf"))
async def process_pdf(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    files = data.get("pdf_files", [])
    
    if not files:
        await message.answer("❌ Hech bir fayl qo'shilmadi.")
        return
    
    await message.answer("⏳ PDF tayyorlanmoqda...")
    
    try:
        from pdf_generator import merge_to_pdf
        pdf_path = await merge_to_pdf(files, bot, message.from_user.id)
        
        from aiogram.types import FSInputFile
        await bot.send_document(message.chat.id, FSInputFile(pdf_path), caption=f"✅ PDF: {len(files)} fayl")
        os.remove(pdf_path)
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)}")
        raise e
    
    await state.clear()
