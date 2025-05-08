async function createMaster(params = {}) {
    try {
        // 1. Получаем и объединяем параметры
        const extensionParams = await getExtensionParams();
        const currentParams = {
            ...extensionParams,
            ...params
        };

        // 2. Валидация
        const required = ['baseUrl', 'bearerToken', 'userToken', 'salonId'];
        const missing = required.filter(p => !currentParams[p]);
        if (missing.length) throw new Error(`Missing: ${missing.join(', ')}`);

        // 3. Нормализация URL
        const cleanBaseUrl = normalizeUrl(currentParams.baseUrl);

        // 4. Заголовки
        const bearerHeaders = {
            'Authorization': `Bearer ${currentParams.bearerToken}`,
            'Accept': 'application/vnd.yclients.v2+json'
        };

        const userTokenHeaders = {
            'Authorization': `Bearer ${currentParams.bearerToken}, User ${currentParams.userToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.api.v2+json'
        };

        // 5. Получаем свободный номер телефона и генерим базовые данные пользователя
        let phoneData = await checkPhone(cleanBaseUrl, currentParams);
        console.log(phoneData)

        // 6. Получаем id сети
        let chainId = await getChain(cleanBaseUrl, currentParams);
        console.log(chainId)

        // 7. Создаем пользователя
        if (currentParams.addUser == true) {
            let user = await createUser(cleanBaseUrl, currentParams, phoneData.number,
                phoneData.email, phoneData.firstname, chainId);
            console.log(user.data?.id);
            await updateUser(cleanBaseUrl, currentParams, user.data?.id, phoneData.number,
                phoneData.email, phoneData.firstname);
        }

        //выбрасываем ошибку если все плохо
    } catch (error) {
        console.error('Ошибка в цепочке:', error);
        throw error;
    }
}

//создание мастера
async function createSalonMaster(baseUrl, params, phone) {
    url = `${baseUrl}/api/v1/company/${params.salonId}/staff/quick`;
}

async function createUser(baseUrl, params, phone, email, firstname, chainId) {
    let url = `${baseUrl}/tester/salon_user`;
    let body =
    {
        "salon_id": `${params.salonId}`,
        "login": `${email}`,
        "phone": `${phone}`,
        "name": `${firstname}`,
        "user_role": "administrator",
        "user_permissions": [
            {
                "slug": "timetable_access",
                "value": true
            },
            {
                "slug": "timetable_position_id",
                "value": 0
            },
            {
                "slug": "timetable_staff_id",
                "value": 0
            },
            {
                "slug": "timetable_last_days_count",
                "value": -1
            },
            {
                "slug": "timetable_schedule_edit_access",
                "value": true
            },
            {
                "slug": "timetable_phones_access",
                "value": true
            },
            {
                "slug": "timetable_transferring_record_access",
                "value": true
            },
            {
                "slug": "timetable_statistics_access",
                "value": true
            },
            {
                "slug": "records_access",
                "value": true
            },
            {
                "slug": "records_clients_access",
                "value": true
            },
            {
                "slug": "records_clients_add_access",
                "value": true
            },
            {
                "slug": "records_autocomplete_access",
                "value": true
            },
            {
                "slug": "records_autocomplete_phones_access",
                "value": true
            },
            {
                "slug": "records_custom_fields_values_access",
                "value": true
            },
            {
                "slug": "records_create_access",
                "value": true
            },
            {
                "slug": "records_edit_access",
                "value": true
            },
            {
                "slug": "records_edit_last_days_count",
                "value": -1
            },
            {
                "slug": "records_edit_client_came_access",
                "value": true
            },
            {
                "slug": "records_edit_full_paid_client_came_access",
                "value": true
            },
            {
                "slug": "records_edit_full_paid_client_confirm_access",
                "value": true
            },
            {
                "slug": "records_services_cost_access",
                "value": true
            },
            {
                "slug": "records_services_discount_access",
                "value": true
            },
            {
                "slug": "records_custom_fields_values_edit_access",
                "value": true
            },
            {
                "slug": "records_edit_date_and_master_access",
                "value": true
            },
            {
                "slug": "records_edit_duration_access",
                "value": true
            },
            {
                "slug": "records_edit_comment_access",
                "value": true
            },
            {
                "slug": "records_edit_services_access",
                "value": true
            },
            {
                "slug": "records_delete_access",
                "value": true
            },
            {
                "slug": "records_delete_client_came_access",
                "value": true
            },
            {
                "slug": "records_delete_paid_access",
                "value": true
            },
            {
                "slug": "records_goods_access",
                "value": true
            },
            {
                "slug": "records_goods_transaction_create_access",
                "value": true
            },
            {
                "slug": "records_goods_transaction_create_last_days_count",
                "value": -1
            },
            {
                "slug": "records_goods_transaction_edit_access",
                "value": true
            },
            {
                "slug": "records_goods_transaction_edit_last_days_count",
                "value": -1
            },
            {
                "slug": "records_goods_cost_access",
                "value": true
            },
            {
                "slug": "records_goods_discount_access",
                "value": true
            },
            {
                "slug": "records_finances_access",
                "value": true
            },
            {
                "slug": "records_finances_last_days_count",
                "value": -1
            },
            {
                "slug": "records_finances_accounts_limited_access",
                "value": 0
            },
            {
                "slug": "records_finances_limited_account_ids",
                "value": []
            },
            {
                "slug": "records_finances_pay_from_deposits_access",
                "value": true
            },
            {
                "slug": "records_consumables_edit_access",
                "value": true
            },
            {
                "slug": "records_clients_statistics_chain_access",
                "value": true
            },
            {
                "slug": "records_clients_statistics_chain_id",
                "value": `${chainId}`
            },
            {
                "slug": "finances_access",
                "value": true
            },
            {
                "slug": "finances_accounts_limited_access",
                "value": 0
            },
            {
                "slug": "finances_accounts_ids",
                "value": []
            },
            {
                "slug": "finances_transactions_access",
                "value": true
            },
            {
                "slug": "finances_transactions_last_days_count",
                "value": -1
            },
            {
                "slug": "finances_transactions_create_access",
                "value": true
            },
            {
                "slug": "finances_transactions_create_last_days_count",
                "value": -1
            },
            {
                "slug": "finances_transactions_edit_access",
                "value": true
            },
            {
                "slug": "finances_transactions_edit_last_days_count",
                "value": -1
            },
            {
                "slug": "finances_transactions_delete_access",
                "value": true
            },
            {
                "slug": "finances_transactions_export_access",
                "value": true
            },
            {
                "slug": "finances_expenses_limited_access",
                "value": 0
            },
            {
                "slug": "finances_expenses_ids",
                "value": []
            },
            {
                "slug": "finances_accounts_access",
                "value": true
            },
            {
                "slug": "finances_accounts_balance_access",
                "value": true
            },
            {
                "slug": "finances_suppliers_access",
                "value": true
            },
            {
                "slug": "finances_suppliers_create_access",
                "value": true
            },
            {
                "slug": "finances_suppliers_edit_access",
                "value": true
            },
            {
                "slug": "finances_suppliers_delete_access",
                "value": true
            },
            {
                "slug": "finances_suppliers_export_access",
                "value": true
            },
            {
                "slug": "finances_expenses_access",
                "value": true
            },
            {
                "slug": "finances_expenses_create_access",
                "value": true
            },
            {
                "slug": "finances_expenses_edit_access",
                "value": true
            },
            {
                "slug": "finances_expenses_delete_access",
                "value": true
            },
            {
                "slug": "finances_kkm_transactions_access",
                "value": true
            },
            {
                "slug": "finances_kkm_settings_access",
                "value": true
            },
            {
                "slug": "finances_kkm_settings_edit_access",
                "value": true
            },
            {
                "slug": "finances_settings_invoicing_access",
                "value": true
            },
            {
                "slug": "finances_settings_invoicing_edit_access",
                "value": true
            },
            {
                "slug": "finances_settings_access",
                "value": true
            },
            {
                "slug": "finances_settings_edit_access",
                "value": true
            },
            {
                "slug": "finances_salary_schemes_access",
                "value": true
            },
            {
                "slug": "finances_salary_access",
                "value": true
            },
            {
                "slug": "finances_salary_no_limit_today_access",
                "value": 1
            },
            {
                "slug": "finances_salary_payroll_access",
                "value": true
            },
            {
                "slug": "finances_salary_payroll_no_limit_today_access",
                "value": 1
            },
            {
                "slug": "finances_salary_staff_access",
                "value": false
            },
            {
                "slug": "finances_salary_staff_id",
                "value": false
            },
            {
                "slug": "finances_salary_staff_no_limit_today_access",
                "value": 1
            },
            {
                "slug": "finances_salary_staff_payroll_access",
                "value": true
            },
            {
                "slug": "finances_salary_staff_payroll_no_limit_today_access",
                "value": 1
            },
            {
                "slug": "finances_period_report_access",
                "value": true
            },
            {
                "slug": "finances_period_report_export_access",
                "value": true
            },
            {
                "slug": "finances_year_report_access",
                "value": true
            },
            {
                "slug": "finances_year_report_export_access",
                "value": true
            },
            {
                "slug": "finances_bill_print_access",
                "value": true
            },
            {
                "slug": "finances_z_report_access",
                "value": true
            },
            {
                "slug": "finances_z_report_no_limit_today_access",
                "value": 1
            },
            {
                "slug": "finances_z_report_export_access",
                "value": true
            },
            {
                "slug": "storages_access",
                "value": true
            },
            {
                "slug": "storages_limited_access",
                "value": 0
            },
            {
                "slug": "storages_ids",
                "value": []
            },
            {
                "slug": "storages_goods_prime_cost_view_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_last_days_count",
                "value": -1
            },
            {
                "slug": "storages_goods_move_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_create_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_create_last_days_count",
                "value": -1
            },
            {
                "slug": "storages_goods_transactions_create_buy_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_create_sale_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_edit_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_edit_last_days_count",
                "value": -1
            },
            {
                "slug": "storages_goods_transactions_edit_buy_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_edit_sale_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_delete_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_export_access",
                "value": true
            },
            {
                "slug": "storages_goods_transactions_types_limited_access",
                "value": 0
            },
            {
                "slug": "storages_goods_transactions_types",
                "value": []
            },
            {
                "slug": "storages_inventory_access",
                "value": true
            },
            {
                "slug": "storages_inventory_create_edit_access",
                "value": true
            },
            {
                "slug": "storages_inventory_delete_access",
                "value": true
            },
            {
                "slug": "storages_inventory_export_access",
                "value": true
            },
            {
                "slug": "storages_remnants_report_access",
                "value": true
            },
            {
                "slug": "storages_remnants_report_export_access",
                "value": true
            },
            {
                "slug": "storages_sales_report_access",
                "value": true
            },
            {
                "slug": "storages_sales_report_export_access",
                "value": true
            },
            {
                "slug": "storages_consumable_report_access",
                "value": true
            },
            {
                "slug": "storages_consumable_report_export_access",
                "value": true
            },
            {
                "slug": "storages_write_off_report_access",
                "value": true
            },
            {
                "slug": "storages_write_off_report_export_access",
                "value": true
            },
            {
                "slug": "storages_turnover_report_access",
                "value": true
            },
            {
                "slug": "storages_turnover_report_export_access",
                "value": true
            },
            {
                "slug": "storages_goods_access",
                "value": true
            },
            {
                "slug": "storages_goods_create_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_title_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_category_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_selling_price_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_cost_price_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_units_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_critical_balance_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_masses_access",
                "value": true
            },
            {
                "slug": "storages_goods_edit_comment_access",
                "value": true
            },
            {
                "slug": "storages_goods_archive_access",
                "value": true
            },
            {
                "slug": "storages_goods_delete_access",
                "value": true
            },
            {
                "slug": "settings_access",
                "value": true
            },
            {
                "slug": "settings_basis_access",
                "value": true
            },
            {
                "slug": "settings_information_access",
                "value": true
            },
            {
                "slug": "settings_users_access",
                "value": true
            },
            {
                "slug": "settings_users_delete_access",
                "value": true
            },
            {
                "slug": "settings_users_create_access",
                "value": true
            },
            {
                "slug": "settings_users_notifications_access",
                "value": true
            },
            {
                "slug": "settings_users_edit_access",
                "value": true
            },
            {
                "slug": "settings_users_limited_access",
                "value": 0
            },
            {
                "slug": "settings_services_access",
                "value": true
            },
            {
                "slug": "settings_services_create_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_title_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_category_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_price_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_image_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_online_seance_date_time_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_online_pay_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_services_related_resource_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_staff_and_duration_access",
                "value": true
            },
            {
                "slug": "settings_services_edit_technological_card_access",
                "value": true
            },
            {
                "slug": "settings_services_delete_access",
                "value": true
            },
            {
                "slug": "settings_staff_access",
                "value": true
            },
            {
                "slug": "settings_staff_create_access",
                "value": true
            },
            {
                "slug": "settings_staff_edit_access",
                "value": true
            },
            {
                "slug": "settings_staff_delete_access",
                "value": true
            },
            {
                "slug": "settings_staff_dismiss_access",
                "value": true
            },
            {
                "slug": "settings_positions_access",
                "value": true
            },
            {
                "slug": "settings_positions_create_access",
                "value": true
            },
            {
                "slug": "settings_positions_delete_access",
                "value": true
            },
            {
                "slug": "settings_schedule_edit_access",
                "value": true
            },
            {
                "slug": "settings_notifications_sms_access",
                "value": true
            },
            {
                "slug": "settings_notifications_email_access",
                "value": true
            },
            {
                "slug": "settings_notifications_templates_access",
                "value": true
            },
            {
                "slug": "settings_webhook_access",
                "value": true
            },
            {
                "slug": "settings_billing_documents_access",
                "value": true
            },
            {
                "slug": "settings_clients_labels_access",
                "value": true
            },
            {
                "slug": "clients_access",
                "value": true
            },
            {
                "slug": "clients_phones_email_access",
                "value": true
            },
            {
                "slug": "clients_card_phone_access",
                "value": true
            },
            {
                "slug": "clients_surname_patronymic_access",
                "value": true
            },
            {
                "slug": "clients_surname_patronymic_edit_access",
                "value": true
            },
            {
                "slug": "clients_edit_access",
                "value": true
            },
            {
                "slug": "clients_loyalty_access",
                "value": true
            },
            {
                "slug": "clients_card_comment_access",
                "value": true
            },
            {
                "slug": "clients_card_comment_edit_access",
                "value": true
            },
            {
                "slug": "clients_delete_access",
                "value": true
            },
            {
                "slug": "clients_export_access",
                "value": true
            },
            {
                "slug": "clients_comments_access",
                "value": true
            },
            {
                "slug": "clients_comments_add_access",
                "value": true
            },
            {
                "slug": "clients_comments_own_edit_access",
                "value": true
            },
            {
                "slug": "clients_comments_other_edit_access",
                "value": true
            },
            {
                "slug": "clients_files_access",
                "value": true
            },
            {
                "slug": "clients_files_upload_access",
                "value": true
            },
            {
                "slug": "clients_files_delete_access",
                "value": true
            },
            {
                "slug": "clients_custom_fields_values_access",
                "value": true
            },
            {
                "slug": "clients_custom_fields_values_edit_access",
                "value": true
            },
            {
                "slug": "clients_visit_staff_id",
                "value": 0
            },
            {
                "slug": "clients_attendance_history_access",
                "value": true
            },
            {
                "slug": "clients_deposits_access",
                "value": true
            },
            {
                "slug": "clients_deposits_create_access",
                "value": true
            },
            {
                "slug": "clients_deposits_topup_access",
                "value": true
            },
            {
                "slug": "clients_deposits_history_access",
                "value": true
            },
            {
                "slug": "clients_loyalty_settings_access",
                "value": true
            },
            {
                "slug": "dashboard_access",
                "value": true
            },
            {
                "slug": "dashboard_overview_access",
                "value": true
            },
            {
                "slug": "dashboard_overview_phones_access",
                "value": true
            },
            {
                "slug": "dashboard_records_access",
                "value": true
            },
            {
                "slug": "dashboard_records_last_days_count",
                "value": -1
            },
            {
                "slug": "dashboard_records_export_access",
                "value": true
            },
            {
                "slug": "dashboard_records_phones_access",
                "value": true
            },
            {
                "slug": "dashboard_messages_access",
                "value": true
            },
            {
                "slug": "dashboard_messages_export_access",
                "value": true
            },
            {
                "slug": "dashboard_messages_phones_access",
                "value": true
            },
            {
                "slug": "dashboard_reviews_access",
                "value": true
            },
            {
                "slug": "dashboard_reviews_delete_access",
                "value": true
            },
            {
                "slug": "dashboard_calls_access",
                "value": true
            },
            {
                "slug": "dashboard_calls_export_access",
                "value": true
            },
            {
                "slug": "dashboard_calls_phones_access",
                "value": true
            },
            {
                "slug": "security_access",
                "value": true
            },
            {
                "slug": "security_2fa_access",
                "value": true
            },
            {
                "slug": "security_export_import_access",
                "value": true
            },
            {
                "slug": "security_data_changes_access",
                "value": true
            },
            {
                "slug": "security_employee_changes_access",
                "value": true
            },
            {
                "slug": "security_logins_access",
                "value": true
            },
            {
                "slug": "medicine_access",
                "value": true
            },
            {
                "slug": "medicine_card_access",
                "value": true
            },
            {
                "slug": "medicine_card_view_access",
                "value": true
            },
            {
                "slug": "medicine_card_print_access",
                "value": true
            },
            {
                "slug": "medicine_card_edit_access",
                "value": true
            },
            {
                "slug": "medicine_appointment_access",
                "value": true
            },
            {
                "slug": "medicine_appointment_view_access",
                "value": true
            },
            {
                "slug": "medicine_appointment_view_settings_position_id",
                "value": 0
            },
            {
                "slug": "medicine_appointment_view_settings_staff_id",
                "value": 0
            },
            {
                "slug": "medicine_appointment_print_access",
                "value": true
            },
            {
                "slug": "medicine_appointment_edit_access",
                "value": true
            },
            {
                "slug": "medicine_appointment_edit_settings_position_id",
                "value": 0
            },
            {
                "slug": "medicine_appointment_edit_settings_staff_id",
                "value": 0
            },
            {
                "slug": "medicine_treatment_plan_access",
                "value": true
            },
            {
                "slug": "medicine_treatment_plan_view_access",
                "value": true
            },
            {
                "slug": "medicine_treatment_plan_print_access",
                "value": true
            },
            {
                "slug": "medicine_treatment_plan_edit_access",
                "value": true
            },
            {
                "slug": "loyalty_access",
                "value": true
            },
            {
                "slug": "loyalty_cards_issue_and_removal_access",
                "value": true
            },
            {
                "slug": "loyalty_cards_manual_transactions_access",
                "value": true
            },
            {
                "slug": "loyalty_abonement_balance_edit_access",
                "value": true
            },
            {
                "slug": "loyalty_abonement_period_edit_access",
                "value": true
            },
            {
                "slug": "loyalty_abonement_history_access",
                "value": true
            },
            {
                "slug": "loyalty_certificate_balance_edit_access",
                "value": true
            },
            {
                "slug": "loyalty_certificate_period_edit_access",
                "value": true
            },
            {
                "slug": "loyalty_certificate_and_abonement_manual_transactions_access",
                "value": true
            },
            {
                "slug": "billing_access",
                "value": true
            },
            {
                "slug": "billing_invoices_access",
                "value": true
            },
            {
                "slug": "tips_access",
                "value": true
            },
            {
                "slug": "tips_setup_access",
                "value": true
            },
            {
                "slug": "online_record_access",
                "value": true
            },
            {
                "slug": "online_record_privacy_policy_access",
                "value": true
            },
            {
                "slug": "auth_enable_check_ip",
                "value": false
            },
            {
                "slug": "auth_list_allowed_ip",
                "value": ""
            },
            {
                "slug": "statistics_access",
                "value": true
            },
            {
                "slug": "send_sms_access",
                "value": true
            },
            {
                "slug": "company_to_chain_add_access",
                "value": true
            }
        ]

    }
    try {
        let response = await fetch(url, {
            method: `POST`,
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        })
        if (response.ok) {
            return await response.json()
        } else {
            throw new Error(`Не удалось создать пользователя: ${response.statusText}`);
        }
    }
    catch(error) {
        throw new Error(`Не удалось создать пользователя: ${error.message}`);
    }
}

async function updateUser(baseUrl, params, userId, phone, email, firstname) {
    const url = `${baseUrl}/settings/user_save`;

    // Формируем данные для отправки
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('salon_id', params.salonId);
    formData.append('firstname', firstname);
    formData.append(`information`, ``);
    formData.append('phone', phone);
    formData.append('email', email);
    formData.append('pass', '123456');
    formData.append('YcField-1', '');
    formData.append('status', '2');
    formData.append('web_push', '1');
    formData.append('web_phone_push', '1');
    formData.append('url_to_set_permissions', '/api/v1/translate/sidebar/languages/');
    formData.append('user_id_to_set_permissions', userId);

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Accept': 'application/json'
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Не удалось задать пароль: ${response.status}`);
        }

        return await response.json();
    } catch {}
}

async function getChain(baseUrl, params) {
    url = `${baseUrl}/api/v1/company/${params.salonId}/`
    try {
        let response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Content-Type': 'application/json'}})
        if (response.ok) {
            let data = await response.json();
            return data.main_group_id
        }
    }
    catch(error) {
        throw new Error(`При получении id сети что то пошло не так: ${error.message}`);
    }
}

function createPhone() {
    return `7${Math.floor(100000000 + Math.random() * 900000000)}`;
}

async function checkPhone(baseUrl, params) {
    let number = createPhone();
    let url = `${baseUrl}/api/v1/company/${params.salonId}/users/?filter[phone]=${number}`;

    try {
        let response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            let data = await response.json();
            if (data.data?.length === 0) {
                return {
                    number: number,
                    email: `qa-gen-${number}@test.com`,
                    firstname: `[QA-GEN USER] ${number}`,
                    status: 'free'
                };
            } else {
                // Рекурсия с проверкой другого номера
                return checkPhone(baseUrl, params);
            }
        } else {
            throw new Error(`Не удалось проверить номер: ${response.statusText}`);
        }
    } catch(error) {
        throw new Error(`Не удалось проверить номер: ${error.message}`);
    }
}

async function addToTimetable() {

}

async function updateMaster() {

}

async function updateAdditionalInfo() {

}

// Вспомогательные функции
function normalizeUrl(url) {
    try {
        const urlObj = new URL(url.includes('://') ? url : `https://${url}`);
        return `${urlObj.protocol}//${urlObj.hostname}`;
    } catch {
        throw new Error('Некорректный URL');
    }
}

async function getExtensionParams() {
    return new Promise(resolve => {
        chrome.storage.local.get(['baseUrl', 'bearerToken', 'salonId', 'userToken'], resolve);
    });
}

// Автозапуск при наличии параметров
if (window.scriptParams) {
    createMaster(window.scriptParams).catch(e => {
        console.error('Автозапуск не удался:', e);
    });
}


// Для ручного вызова
window.createMaster = createMaster;