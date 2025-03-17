import sys
import pandas as pd

from webapp import executor

sys.path.append('../preprocess')
from preprocess.Ultility_Funcs_data.Step1_HPC_GetStudyIDSource import *
from preprocess.Ultility_Funcs_data.Step2_GetPerPatientData_Medicaid_HealthClaims import *
from preprocess.Ultility_Funcs_data.Step3A_HPC_Get_PerMonthData_withCleanCodes import *
from preprocess.Ultility_Funcs_data.Step3B_HPC_Get_PerMonthData_withCleanCodes_onlymedicare import *
from preprocess.Ultility_Funcs_data.Step3C_HPC_Get_PerMonthData_withCleanCodes_onlymedicaid import *
from preprocess.Ultility_Funcs_data.Step4A_Get_Cancer_SiteDateType import *
from preprocess.Ultility_Funcs_data.Step4B_GetEventType_addNewothers import *
from preprocess.Ultility_Funcs_data.Step5A_GetEnrollmentMonths import *
from preprocess.Ultility_Funcs_data.Step5B_GetPredictionMonths import *
from preprocess.Ultility_Funcs_data.Step8A_Get_PatientLevelCharateristics import *
from preprocess.Ultility_Funcs_data.Step10A_Get_PerPatient_UniqueCodes_AllEnrolls import *
from preprocess.Ultility_Funcs_data.Step10B_Get_PerMonth_CCSDiag_AllEnrolls import *
from preprocess.Ultility_Funcs_data.Step10C_Get_PerMonth_CCSProc_AllEnrolls import *
from preprocess.Ultility_Funcs_data.Step10D_Get_PerMonth_DM3SPE_AllEnrolls import *
from preprocess.Ultility_Funcs_data.Step10F_Get_PerMonth_VAL2NDROOT_AllEnrolls import *
from preprocess.Ultility_Funcs_data.Step11A_Get_ModelReady_SelectedGroupFeature import *
from preprocess.Ultility_Funcs_data.Step11B_Get_ModelReady_BinaryCharFeatures import *
from preprocess.Ultility_Funcs_data.Step11C_Get_ModelReady_TransformationFeature import *
from preprocess.Ultility_Funcs_data.Step11D_Get_ModelReady_Combed_Features import *
from preprocess.Ultility_Funcs_data.Step11E_merge_all import *


def preprocess_data(user_name, num_data, indir, outdir, metacsv, mecareClaims, mecareEnroll, mecaidClaims,
                    mecaidClaims2, mecaidEnroll, month_len_medicaid, month_len_medicare, start_medicaid,
                    start_medicare, drug_code):
    ########################
    #check parameters first#
    ########################
    check_numdata(num_data)
    check_matched_files(num_data, mecareClaims, mecareEnroll, mecaidClaims, mecaidClaims2, mecaidEnroll)

    if num_data == "0":
        check_both(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare)
        int_check(month_len_medicaid)
        int_check(month_len_medicare)

    if num_data == "1":
        check_medicare1(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare)
        int_check(month_len_medicare)

    if num_data == "2":
        check_medicaid2(month_len_medicaid, month_len_medicare, start_medicaid, start_medicare)
        int_check(month_len_medicaid)

    ##########################
    #start preprocessing data#
    ##########################
    if num_data == "0":
        Step1_GetStudyIDSource(user_name, indir, outdir, metacsv, mecareClaims, mecaidClaims, mecaidClaims2)
        Step2_GetPerPatientData_Medicaid_HealthClaims(user_name, indir, outdir, mecareClaims, mecaidClaims, mecaidClaims2)
        Step3A_HPC_Get_PerMonthData_withCleanCodes(user_name, indir, outdir, mecareClaims, mecaidClaims, mecaidClaims2, drug_code)
    elif num_data == "1":
        Step1_GetStudyIDSource1(user_name, indir, outdir, metacsv, mecareClaims)
        Step2_GetPerPatientData_Medicaid_HealthClaims1(user_name, indir, outdir, mecareClaims)
        Step3B_HPC_Get_PerMonthData_withCleanCodes_onlymedicare(user_name, indir, outdir, mecareClaims, drug_code)
    elif num_data == "2":
        Step1_GetStudyIDSource2(user_name, indir, outdir, metacsv, mecaidClaims, mecaidClaims2)
        Step2_GetPerPatientData_Medicaid_HealthClaims2(user_name, indir, outdir, mecaidClaims, mecaidClaims2)
        Step3C_HPC_Get_PerMonthData_withCleanCodes_onlymedicaid(user_name, indir, outdir, mecaidClaims, mecaidClaims2, drug_code)
    Step4A_Get_Cancer_SiteDateType(user_name, indir, outdir, metacsv)
    Step4B_GetEventType_addNewothers(user_name, indir, outdir, metacsv)
    ## No step4c becuase we do not have labels
    if num_data == "0":
        Step5A_GetEnrollmentMonths(user_name, indir, outdir, mecaidEnroll, month_len_medicaid, start_medicaid, mecareEnroll, month_len_medicare, start_medicare)
    elif num_data == "1":
        Step5A_GetEnrollmentMonths1(user_name, indir, outdir, mecareEnroll, month_len_medicare, start_medicare)
    elif num_data == "2":
        Step5A_GetEnrollmentMonths2(user_name, indir, outdir, mecaidEnroll, month_len_medicaid, start_medicaid)

    Step5B_GetPredictionMonths(user_name, indir, outdir, metacsv)
    ## skip 5C due to no label
    Step8A_Get_PatientLevelCharateristics(user_name, indir, outdir,metacsv)
    ## skip 8B_get_labels.py 8C_merge_8Aand4B.py
    Step10A_Get_PerPatient_UniqueCodes_AllEnrolls(user_name, outdir)
    Step10B_Get_PerMonth_CCSDiag_AllEnrolls(user_name, indir, outdir)
    Step10C_Get_PerMonth_CCSProc_AllEnrolls(user_name, indir, outdir)
    if drug_code == 'DM3_SPE':
        Step10D_Get_PerMonth_DM3SPE_AllEnrolls(user_name, indir, outdir)
    else:
        Step10F_Get_PerMonth_VAL2NDROOT_AllEnrolls(user_name, indir, outdir)
    Step11A_Get_ModelReady_SelectedGroupFeature(user_name, indir, outdir, drug_code)
    Step11B_Get_ModelReady_BinaryCharFeatures(user_name, outdir)
    Step11C_Get_ModelReady_TransformationFeature(user_name, outdir, drug_code)
    Step11D_Get_ModelReady_Combed_Features(user_name, outdir, drug_code)
    Step11E_merge_all(user_name, outdir, drug_code)


def summary_stats(job_dir: str):
    """generates summary statistics for a merged data file (patientlevel_prediction_merged_pt_chr.csv)"""
    out_dir = os.path.join(job_dir, 'output')
    for dir_path, dir_names, file_names in os.walk(out_dir):
        for file in file_names:
            if file.startswith('All_11E_'):
                features = pd.read_pickle(os.path.join(dir_path, file))
            elif file.startswith('8_PatientLevel_char_'):
                patients = pd.read_excel(os.path.join(dir_path, file))
    stats = {
        "num_patients": len(patients),
        "num_patient_months": len(features),
        "num_features": len(features.columns)
    }
    return stats
