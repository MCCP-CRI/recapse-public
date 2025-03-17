from prediction.Ultility_Funcs.DataLoader1 import load_rdata, load_pythondata
from prediction.Ultility_Funcs.TrainTest_Funcs import prediction, patient_level_prediction
# from prediction.Ultility_Funcs.Performance_Func import compute_performance_binary,compute_month_diff_perf
import pandas as pd
from functools import reduce
import joblib
import os
from webapp import translations, executor


def predict(feature_sets, SBCE_col, selected_model, input_name, chr_name, cutoff_ori, method, outPath, inPath):
    model_name = 'XGB'  # args['mn']
    ds_indxes = int(3)  # args['ds']
    search_alg = 'Grid'  # args['ps']
    train_sample_type = 'nonobv'  # args['ts']
    # path_input = args['indir']
    path_output = "prediction_results"  # args['outdir']
    modelPath = "./prediction/Saved_XGBoost"  # args['modeldir']

    # Data dir
    data_dir1 = inPath + "/"
    data_dir2 = inPath + "/"  # inpuit of chr file
    data_dir3 = modelPath + "/" + feature_sets + "/" + SBCE_col + "/" + model_name + "/" + "DS" + str(
        ds_indxes) + '/' + train_sample_type + '/' + search_alg + '/'
    data_dir4 = data_dir3 + 'Saved_Model/' + selected_model + "/"

    outdir = outPath + '/'  # + SBCE_col + "/" +selected_model + "/"

    if not os.path.exists(outdir):
        # Create a new directory because it does not exist
        os.makedirs(outdir)
        print("Created directory " + outdir)

        ####################
    # check parameters #
    ####################
    cutoff = round(cutoff_ori, 1)
    if cutoff != cutoff_ori:
        print(
            "The cutoff value exceeding two decimal places will be rounded to one decimal places, now using cutoff of ",
            cutoff)
    if cutoff >= 1 or cutoff < 0:
        raise ValueError("The cutoff value should be larger than 0 and smaller than 1")
    if method > 2:
        raise ValueError(
            "Parameter -method must be 0, 1 or 2 (0 for both patient- and month-level prediction, 1 for only patient-level prediction, and 2 for only month-level prediction)")

    if not isinstance(method, int):
        raise ValueError("Parameter -method must be an integer")
    if selected_model not in ["TopF_Model", "Full_Model"]:
        raise ValueError("Wrong value for -sm, please use TopF_Model or Full_Model")
    if feature_sets not in ['CCSandVAL2nd', 'CCSandDM3SPE']:
        raise ValueError("Wrong value for -sm, please use CCSandVAL2nd or CCSandDM3SPE")
    if SBCE_col not in ['SBCE', 'SBCE_Excluded_DeathPts']:
        raise ValueError("Wrong value for -sm, please use SBCE or SBCE_Excluded_DeathPts")

    ####################################################################################################
    # 1. Load data
    ####################################################################################################
    # Load test data
    test_X1, test_ID1 = load_pythondata(data_dir1,
                                        input_name)  # load_rdata(data_dir1,'test_neg_data.rda','test_neg_df',label_col)
    test_X = test_X1
    test_ID = test_ID1

    ################################################################################
    # 2. Prediction
    ################################################################################
    # Load model
    if selected_model == "TopF_Model":
        trained_model = joblib.load(data_dir4 + model_name + "_TopFeature_model.pkl")  # topFmodel
        import_features_df = pd.read_csv(data_dir4 + "importance.csv")
        import_features = list(import_features_df['Feature'])
        test_X = test_X[import_features]
    elif selected_model == "Full_Model":
        trained_model = joblib.load(data_dir4 + model_name + "_Fullmodel.pkl")  # Fullmodel

    # Prediction month-level
    # print(trained_model)
    pred_df_m = prediction(trained_model, test_X, test_ID, cutoff)
    if method == 0 or method == 2:
        pred_df_m.to_csv(outdir + 'monthlevel_prediction.csv', index=False)

    # Prediction Patient-level (3month consecutive method)
    thres_list = [cutoff]  # [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    pred_df_p_list = []
    for thres in thres_list:
        pred_df_p = patient_level_prediction(pred_df_m, thres, pred_method="3month")
        # sufix_col =  str(thres).replace('.','')
        # pred_df_p.rename(columns = {'pred_label': 'pred_label_th' + sufix_col,
        #                             'pred_month': 'pred_month_th' + sufix_col,
        #                             'RAW_Month_Diff': 'RAW_Month_Diff_th' + sufix_col,
        #                             'ABS_Month_Diff': 'ABS_Month_Diff_th' + sufix_col},
        #                  inplace = True)
        pred_df_p_list.append(pred_df_p)

    pred_df_p_all = reduce(lambda x, y: pd.merge(x, y, on=['study_id', ]), pred_df_p_list)
    # pred_df_p_all.to_csv(outdir + 'patientlevel_prediction.csv', index = False)

    ### new added code by Q.Q.
    # Load SBCE month label patient -level
    pts_level_char_df = pd.read_excel(data_dir2 + str(chr_name))

    # pts_level_char_df['study_id'] = 'ID' + pts_level_char_df['study_id'].astype(str)
    pts_level_char_df = pts_level_char_df.astype({'study_id': 'string'})

    merged_df = pd.merge(pts_level_char_df, pred_df_p_all, on='study_id', how='outer')
    merged_df.to_csv(outdir + 'patientlevel_prediction_merged_pt_chr.csv', index=False)

    print("Prediction finished")


def summary_stats(job_dir: str):
    """generates summary statistics for a merged data file (patientlevel_prediction_merged_pt_chr.csv)"""
    out_dir = os.path.join(job_dir, 'output')
    df = pd.read_csv(os.path.join(out_dir, 'patientlevel_prediction_merged_pt_chr.csv'))
    stats = {'count': len(df)}
    positives = df[df['pred_label'] == 1]
    stats['recurrences'] = len(positives)
    # count by race
    stats['by_race'] = {}
    race_translation = translations.get_race_translation()
    total_race_counts = df.merge(race_translation, on='Race')['Translation'].value_counts()
    positive_race_counts = positives.merge(race_translation, on='Race')['Translation'].value_counts()
    for race in total_race_counts.index:
        tc = total_race_counts[race]
        pc = 0
        if race in positive_race_counts:
            pc = positive_race_counts[race]
        stats['by_race'][race] = [tc, pc]
    # count by stage
    stats['by_stage'] = {}
    stage_translation = translations.get_stage_group_translation()
    total_stage_counts = df.merge(stage_translation, on='Stage')['Translation'].value_counts()
    positive_stage_counts = positives.merge(stage_translation, on='Stage')['Translation'].value_counts()
    for stage in total_stage_counts.index:
        tc = total_stage_counts[stage]
        pc = 0
        if stage in positive_stage_counts:
            pc = positive_stage_counts[stage]
        stats['by_stage'][stage] = [tc, pc]
    # count by year dx
    stats['by_year'] = {}
    total_year_counts = df['Date_dx'].map(lambda x: x.split('/')[2]).value_counts()
    positive_year_counts = positives['Date_dx'].map(lambda x: x.split('/')[2]).value_counts()
    for year in total_year_counts.index.sort_values():
        tc = total_year_counts[year]
        pc = 0
        if year in positive_year_counts:
            pc = positive_year_counts[year]
        stats['by_year'][year] = [tc, pc]
    # count by age at first dx
    stats['by_age'] = {}
    # calculate age at dx
    date_dx_df = df['Date_dx'].map(convert_date)
    date_birth_df = df['date_Birth'].map(convert_date)
    age_dx_df = (date_dx_df - date_birth_df) // 10000
    # calculate counts for age bins
    age_dx_bins = age_dx_df.map(bin_age)
    age_bin_counts = age_dx_bins.value_counts()
    # calculate age at dx for positive cases
    positive_date_dx_df = positives['Date_dx'].map(convert_date)
    positive_date_birth_df = positives['date_Birth'].map(convert_date)
    positive_age_dx_df = (positive_date_dx_df - positive_date_birth_df) // 10000
    # calculate counts for age bins
    positive_age_dx_bins = positive_age_dx_df.map(bin_age)
    positive_age_bin_counts = positive_age_dx_bins.value_counts()
    for age_group in age_bin_counts.index.sort_values():
        tc = age_bin_counts[age_group]
        pc = 0
        if age_group in positive_age_bin_counts:
            pc = positive_age_bin_counts[age_group]
        stats['by_age'][age_group] = [tc, pc]
    return stats


def convert_date(date: str):
    parts = date.split('/')
    return int(parts[2].rjust(4, '0') + parts[0].rjust(2, '0') + parts[1].rjust(2, '0'))


def bin_age(age: int):
    if age <= 49:
        return '0-49'
    elif age <= 64:
        return '50-64'
    elif age <= 74:
        return '65-74'
    else:
        return '75+'
