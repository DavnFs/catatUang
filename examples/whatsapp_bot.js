const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// Configuration
const WEBHOOK_URL = 'https://your-app.vercel.app/api/webhook'; // Replace with your URL

/**
 * WhatsApp Bot untuk CatatUang
 * Otomatis forward pesan #kategori jumlah keterangan ke serverless API
 */
class CatatUangBot {
    constructor(webhookUrl) {
        this.webhookUrl = webhookUrl;
        this.client = new Client({
            authStrategy: new LocalAuth(),
            puppeteer: {
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            }
        });
        
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        // QR Code untuk login
        this.client.on('qr', (qr) => {
            console.log('📱 Scan QR code dengan WhatsApp:');
            qrcode.generate(qr, { small: true });
        });
        
        // Bot ready
        this.client.on('ready', () => {
            console.log('🤖 CatatUang Bot siap!');
            console.log('📝 Format: #kategori jumlah keterangan');
            console.log('📊 Kirim "laporan" untuk report');
            console.log('🔗 Webhook:', this.webhookUrl);
        });
        
        // Authenticated
        this.client.on('authenticated', () => {
            console.log('✅ WhatsApp authenticated!');
        });
        
        // Auth failure
        this.client.on('auth_failure', (msg) => {
            console.error('❌ Authentication failed:', msg);
        });
        
        // Disconnected
        this.client.on('disconnected', (reason) => {
            console.log('❌ WhatsApp disconnected:', reason);
        });
        
        // Message handler
        this.client.on('message', async (msg) => {
            await this.handleMessage(msg);
        });
    }
    
    async handleMessage(msg) {
        const text = msg.body.trim();
        const chatId = msg.from;
        
        console.log(`📨 [${new Date().toLocaleTimeString()}] ${chatId}: ${text}`);
        
        try {
            // Expense message (#kategori jumlah keterangan)
            if (text.startsWith('#')) {
                await this.handleExpenseMessage(msg, text);
            }
            // Report request
            else if (text.toLowerCase() === 'laporan' || text.toLowerCase() === 'report') {
                await this.handleReportRequest(msg);
            }
            // Help message
            else if (text.toLowerCase() === 'help' || text === '?') {
                await this.sendHelpMessage(msg);
            }
            // Ignore other messages
            
        } catch (error) {
            console.error('❌ Error handling message:', error);
            await msg.reply('❌ Terjadi kesalahan. Coba lagi nanti.');
        }
    }
    
    async handleExpenseMessage(msg, text) {
        try {
            console.log(`💰 Processing expense: ${text}`);
            
            // Send to webhook
            const response = await axios.post(this.webhookUrl, { text }, {
                timeout: 10000,
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = response.data;
            
            if (result.status === 'success') {
                const { data } = result;
                const replyText = 
                    `✅ *Data berhasil disimpan!*\n\n` +
                    `📝 *Kategori:* ${data.kategori}\n` +
                    `💰 *Jumlah:* Rp ${data.jumlah.toLocaleString('id-ID')}\n` +
                    `📋 *Keterangan:* ${data.keterangan}\n` +
                    `🕒 *Waktu:* ${data.timestamp}`;
                
                await msg.reply(replyText);
            } else {
                await msg.reply(`❌ *Error:* ${result.message}\n\n📖 Format: #kategori jumlah keterangan`);
            }
            
        } catch (error) {
            console.error('Error processing expense:', error);
            await msg.reply('❌ Gagal menyimpan data. Pastikan server berjalan.');
        }
    }
    
    async handleReportRequest(msg) {
        try {
            console.log('📊 Generating report...');
            
            // Get report from API
            const response = await axios.get(`${this.webhookUrl.replace('/webhook', '/report')}`, {
                timeout: 15000
            });
            
            const result = response.data;
            
            if (result.status === 'success') {
                const { summary } = result;
                
                let reportText = '📊 *LAPORAN PENGELUARAN* 📊\n\n';
                
                // Category breakdown
                const categories = summary.categories || {};
                for (const [kategori, total] of Object.entries(categories)) {
                    const count = summary.category_counts?.[kategori] || 0;
                    reportText += `• *${kategori}:* Rp ${total.toLocaleString('id-ID')} (${count}x)\n`;
                }
                
                reportText += `\n💰 *Total:* Rp ${summary.total_expense.toLocaleString('id-ID')}\n`;
                reportText += `📝 *Transaksi:* ${summary.total_transactions}\n\n`;
                reportText += `🕒 *Dibuat:* ${new Date().toLocaleString('id-ID')}`;
                
                await msg.reply(reportText);
                
            } else {
                await msg.reply(`❌ *Error:* ${result.message}`);
            }
            
        } catch (error) {
            console.error('Error generating report:', error);
            await msg.reply('❌ Gagal membuat laporan. Pastikan server berjalan.');
        }
    }
    
    async sendHelpMessage(msg) {
        const helpText = 
            `🤖 *CatatUang Bot*\n\n` +
            `📝 *Format pengeluaran:*\n` +
            `#kategori jumlah keterangan\n\n` +
            `📋 *Contoh:*\n` +
            `• #jajan 15000 bakso\n` +
            `• #transport 25000 ojek ke kantor\n` +
            `• #makan 30000 nasi padang\n` +
            `• #kopi 12000 es kopi susu\n\n` +
            `📊 *Perintah lain:*\n` +
            `• "laporan" - Lihat laporan pengeluaran\n` +
            `• "help" - Bantuan ini\n\n` +
            `💡 *Tips:* Kategori harus satu kata tanpa spasi`;
        
        await msg.reply(helpText);
    }
    
    start() {
        console.log('🚀 Starting CatatUang WhatsApp Bot...');
        console.log('🔗 Webhook URL:', this.webhookUrl);
        this.client.initialize();
    }
}

// Start bot
const bot = new CatatUangBot(WEBHOOK_URL);
bot.start();

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down bot...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down bot...');
    process.exit(0);
});
