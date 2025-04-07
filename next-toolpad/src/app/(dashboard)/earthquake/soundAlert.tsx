import { useCallback } from 'react';

type SoundType = 'beep' | 'alarm' | 'notification' | 'chime';
type NotificationType = 'success' | 'error' | 'warning';

const SoundAlert = () => {
    // สร้างเสียง Beep ง่ายๆ
    const playBeep = useCallback(() => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.type = 'sine';
        oscillator.frequency.value = 800;
        gainNode.gain.value = 0.1;

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.start();
        setTimeout(() => {
            oscillator.stop();
        }, 200);
    }, []);

    // สร้างเสียง Alarm
    const playAlarm = useCallback(() => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.type = 'sine';
        gainNode.gain.value = 0.1;

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        const time = audioContext.currentTime;
        oscillator.frequency.setValueAtTime(800, time);
        oscillator.frequency.exponentialRampToValueAtTime(1600, time + 0.5);
        oscillator.frequency.exponentialRampToValueAtTime(800, time + 1);

        oscillator.start(time);
        oscillator.stop(time + 1.5);
    }, []);

    // สร้างเสียง Notification
    const playNotification = useCallback((type: NotificationType) => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        gainNode.gain.value = 0.1;
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        const time = audioContext.currentTime;

        switch (type) {
            case 'success':
                oscillator.type = 'triangle';
                oscillator.frequency.setValueAtTime(523.25, time); // C
                oscillator.frequency.setValueAtTime(659.25, time + 0.1); // E
                oscillator.frequency.setValueAtTime(783.99, time + 0.2); // G
                break;
            case 'error':
                oscillator.type = 'square';
                oscillator.frequency.setValueAtTime(392, time); // G
                oscillator.frequency.setValueAtTime(311.13, time + 0.1); // D#
                break;
            case 'warning':
                oscillator.type = 'sawtooth';
                oscillator.frequency.setValueAtTime(440, time); // A
                oscillator.frequency.setValueAtTime(440, time + 0.1);
                oscillator.frequency.setValueAtTime(349.23, time + 0.2); // F
                break;
        }

        oscillator.start(time);
        oscillator.stop(time + 0.3);
    }, []);

    // สร้างเสียง Chime
    const playChime = useCallback(() => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();

        // เสียงหลัก
        const mainOsc = audioContext.createOscillator();
        mainOsc.type = 'sine';
        mainOsc.frequency.value = 1046.50; // C สูง

        const mainGain = audioContext.createGain();
        mainGain.gain.setValueAtTime(0.1, audioContext.currentTime);
        mainGain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 2);

        mainOsc.connect(mainGain);
        mainGain.connect(audioContext.destination);

        // เสียงฮาร์โมนิค
        const harmonicOsc = audioContext.createOscillator();
        harmonicOsc.type = 'sine';
        harmonicOsc.frequency.value = 1318.51; // E

        const harmonicGain = audioContext.createGain();
        harmonicGain.gain.setValueAtTime(0.05, audioContext.currentTime);
        harmonicGain.gain.exponentialRampToValueAtTime(0.005, audioContext.currentTime + 2);

        harmonicOsc.connect(harmonicGain);
        harmonicGain.connect(audioContext.destination);

        mainOsc.start();
        harmonicOsc.start();

        mainOsc.stop(audioContext.currentTime + 2);
        harmonicOsc.stop(audioContext.currentTime + 2);
    }, []);

    // เลือกเล่นเสียงตามประเภท
    const playSound = useCallback((type: SoundType, notificationType?: NotificationType) => {
        switch (type) {
            case 'beep':
                playBeep();
                break;
            case 'alarm':
                playAlarm();
                break;
            case 'notification':
                if (notificationType) playNotification(notificationType);
                break;
            case 'chime':
                playChime();
                break;
        }
    }, [playBeep, playAlarm, playNotification, playChime]);

    return (
        <div className="sound-alert-container">
            <h2>Sound Alert Examples</h2>
            <div className="button-group">
                <button onClick={() => playSound('beep')}>Beep</button>
                <button onClick={() => playSound('alarm')}>Alarm</button>
                <button onClick={() => playSound('chime')}>Chime</button>
            </div>
            <div className="button-group">
                <button onClick={() => playSound('notification', 'success')}>Success</button>
                <button onClick={() => playSound('notification', 'error')}>Error</button>
                <button onClick={() => playSound('notification', 'warning')}>Warning</button>
            </div>
        </div>
    );
};

export default SoundAlert;