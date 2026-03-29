import Phaser from 'phaser';

export default class Location-component extends Phaser.Scene {
    constructor() {
        super({
            key: 'LocationComponent'
        });
    }

    create() {
        // Background image
        const bg = this.add.image(0, 0, 'bg');

        // Title
        const titleStyle = {
            fontFamily: 'Ancient',
            fontSize: '32px',
            color: '#ffffff'
        };
        this.add.text('Location Confirmation');

        // Instructions
        const instructionsStyle = {
            fontFamily: 'Ancient',
            fontSize: '18px',
            fill: '#ffcc00,
            wordWrap: { width: '220', padding: '20px' }
        };
        instructionsStyle.setText('Click and drag to confirm location, Click again to cancel');

        // Confirm button
        const confirmButton = this.add.image(0, 0, 'bg', 'button')
            .setInteractive()
            .setOrigin(0, 0);
        confirmButton.setVisible = true;
        confirmButton.text = 'Confirm';

        // hint text
        const hintTextStyle = {
            fontFamily: 'Ancient',
            fontSize: '16px',
            fill: '#999',
        };
        hintTextStyle.setText('Drag to confirm or cancel');

        // Create graphics
        this.createGraphics();
    }

    create() {
        this.add.image(0, 0, 'bg');

        // Create game text
        const gameText = this.add.text(0, 0, '  GameText');
        gameText.setOrigin(400, 200);
        gameText.text = 'Location confirmation test';
        gameText.setColor('#ffffff');
        gameText.setVisible = false;
    }

}
