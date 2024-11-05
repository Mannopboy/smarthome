async function toggleChiroq(xona) {
    try {
        const response = await fetch(`/${xona}/chiroq`, {
            method: 'POST'
        });
        const data = await response.json();
        const chiroqStatus = data.chiroq ? 'Yoqilgan' : 'O\'chirilgan';
        document.getElementById(`${xona}-chiroq`).innerText = `Chiroq: ${chiroqStatus}`;
    } catch (error) {
        console.error(`Chiroqni almashtirishda xato: ${error}`);
    }
}

async function toggleEshik(xona) {
    try {
        const response = await fetch(`/${xona}/eshik`, {
            method: 'POST'
        });
        const data = await response.json();
        const eshikStatus = data.eshik ? 'Ochiq' : 'Yopiq';
        document.getElementById(`${xona}-eshik`).innerText = `Eshik: ${eshikStatus}`;
    } catch (error) {
        console.error(`Eshikni almashtirishda xato: ${error}`);
    }
}
