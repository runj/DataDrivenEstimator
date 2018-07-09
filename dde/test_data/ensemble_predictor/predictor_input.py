predictor_model(embedding_size=512, depth=3, scale_output=0.05,
                padding=True, padding_final_size=20,
                add_extra_atom_attribute=True, add_extra_bond_attribute=True,
                mol_conv_inner_activation='tanh',
                mol_conv_outer_activation='softmax',
                hidden=50, hidden_activation='tanh',
                output_activation='linear', output_size=1,
                lr=0.01, optimizer='adam', loss='mse',
                dropout_rate_inner=0.0, dropout_rate_outer=0.10, dropout_rate_hidden=0.10,
                dropout_rate_output=0.0, n_model =1000)