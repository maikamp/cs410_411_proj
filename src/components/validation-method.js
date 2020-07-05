import React, { Component } from 'react';
import javax.swing.*;
import java.awt.event.*;

public class LoginTaskMaster extends JFrame{
	public static void main (String [] args){
		LoginTaskMaster new_frame = new LoginTaskMaster();
	}
	JButton login_button = new JButton ("Login");
	JPanel panel = new JPanel();
	JLabel user_label = new JLabel("ID");
	JLabel password_label = new JLabel("password");
	JTextField user = new JTextField (15);
	JPasswordField pass = new JPasswordField(15);
	LoginTaskMaster(){
		super("Login Form");
		setSize(300,200);
		setLocation(500,280);
		setResizable(true);
		panel.setLayout(null);
		user_label.setBounds(40,30,150,20);
		password_label.setBounds(40,65,150,20);
		user.setBounds(70,30,150,20);
		pass.setBounds(70,65,150,20);
		login_button.setBounds(110,100,80,20);
		
		//Adding all to layouts
		panel.add(user_label);
		panel.add(password_label);
		panel.add(login_button);
		panel.add(user);
		panel.add(pass);
		getContentPane().add(panel);

		setDefaultCloseOPeration(JFrame.EXIT_ON_CLOSE);
		setVisible(true);
		loginpage();
}
//login form main page 
public void loginpage(){
	login_button.addActionListener(new ActionListener()){
		public void actionPerformed (ActionEvent ae)
		{
			//checking on every input
			if (validateFields()){
				string userid = user.getText();
				string password = pass.getText();
			if (userid.equals("abc") && password.equals("12345")){
				mainwindowframe regFace = new mainwindowframe();
				regFace.setVisible(true);
				dispose();
} else{
	//Reset the boxes if wrong input
	JOPtionPane.showMessageDialog(null,"Wrong password/Username");
	user.setText("");
	pass.setText("");
	user.requestFocus();
	}}}};
	
	public boolean validateFields(){
		if(!validateField(user,"Please enter an id")){
			return false;
}else if (!validatepassword(pass,"Please enter password greater than 0 length")){
	return false;
}else {
	return true;
}
}

public boolean validateField(JTextField f, string errormsg){
	if(f.getText().equals(""))
		return failedMessage(f,errormsg);
	else
		return true;
}

public boolean validatepassword(JTextFieldf, string errormsg){
	try{
		System.out.println(Integer.parselnt(f.getText()));
		if (Integer.parselnt(f.getText())> 0)
		return true;
} catch (Exception e) {
	//if conversion failed or input was < 0
}
	return failedMessage(f, errormsg);
}

public boolean failedMessage (JTextField f, string errormsg){
	JOPtionPane.showMessageDialog(null,errormsg);
	f.requestFocus();
	return false;
}

class mainwindowframe extends JFrame{
	public static void main (string[] args){
		mainwindowframe frameTabel = new mainwindowframe();
	}
	JLabel welcome = new JLabel(" welcome to a Frame");
	JPanel panel = new JPanel ("Welcome to a new frame");
	JPanel panel = new JPanel();
	mainwindowframe(){
		super("Welcome");
		setSize(300,200);
		setLocation(500,280);
		panel.setLayout(null);
		welcome.setBounds(70,50,150,60);
		panel.add(welcome);
		getContentPane().add(panel);

	setDefaultCloseOPeration(JFrame.EXIT_ON_CLOSE);
		setVisible(true);
	}
}
