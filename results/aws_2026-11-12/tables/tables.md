# Tables of the AWS run of 12 Nov 2026

Built by make_tables.py from the raw files of this folder.

## Online SMPC time and memory, one party per c6i.large node

File: `tables/table1_smpc_online_grid.csv`

| n | k | p_bits | ssl | trials | online_mean_ms | online_sd_ms | online_ci95_ms | online_median_ms | online_p95_ms | eval_mean_ms | recon_mean_ms | sharing_mean_ms | peak_rss_mean_mb | peak_rss_max_mb | peak_rss_party0_mb | parties_with_mem_file | sent_per_party_per_trial_mean_mb | sent_per_party_per_trial_max_mb | oracle_match | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 10000 | 64 | 0 | 100 | 8.3687 | 0.5040 | 0.1000 | 8.3960 | 9.0928 | 2.4745 | 5.8942 | 27.35 | 47.14 | 47.31 | 47.13 | 4 | 0.4006 | 0.4007 | 100/100 | smpc_online/n4_k10000/trials_default_n4_k10000.csv |
| 4 | 50000 | 64 | 0 | 100 | 42.21 | 4.7185 | 0.9361 | 42.34 | 50.46 | 12.95 | 29.26 | 143.58 | 72.73 | 73.18 | 73.18 | 4 | 2.0005 | 2.0006 | 100/100 | smpc_online/n4_k50000/trials_default_n4_k50000.csv |
| 8 | 10000 | 64 | 0 | 100 | 13.47 | 0.6997 | 0.1388 | 13.29 | 14.70 | 5.8772 | 7.5909 | 82.09 | 54.41 | 54.64 | 54.43 | 8 | 1.0016 | 1.0017 | 100/100 | smpc_online/n8_k10000/trials_default_n8_k10000.csv |
| 8 | 50000 | 64 | 0 | 100 | 65.01 | 1.4591 | 0.2895 | 64.77 | 66.76 | 28.64 | 36.37 | 418.35 | 108.25 | 108.77 | 108.77 | 8 | 5.0013 | 5.0015 | 100/100 | smpc_online/n8_k50000/trials_default_n8_k50000.csv |
| 12 | 10000 | 64 | 0 | 100 | 20.30 | 1.2712 | 0.2522 | 20.36 | 22.25 | 8.5093 | 11.79 | 143.40 | 61.28 | 61.61 | 61.50 | 12 | 1.6025 | 1.6027 | 100/100 | smpc_online/n12_k10000/trials_default_n12_k10000.csv |
| 12 | 50000 | 64 | 0 | 100 | 110.04 | 18.30 | 3.6309 | 105.41 | 123.77 | 43.38 | 66.66 | 749.99 | 139.83 | 140.53 | 140.17 | 12 | 8.0021 | 8.0024 | 100/100 | smpc_online/n12_k50000/trials_default_n12_k50000.csv |
| 16 | 10000 | 64 | 0 | 100 | 37.18 | 2.6885 | 0.5334 | 37.24 | 41.46 | 11.38 | 25.80 | 214.83 | 69.20 | 69.54 | 69.47 | 16 | 2.2034 | 2.2038 | 100/100 | smpc_online/n16_k10000/trials_default_n16_k10000.csv |
| 16 | 50000 | 64 | 0 | 100 | 175.13 | 11.95 | 2.3718 | 174.44 | 189.13 | 56.24 | 118.89 | 1082.43 | 172.92 | 174.72 | 174.72 | 16 | 11.00 | 11.00 | 100/100 | smpc_online/n16_k50000/trials_default_n16_k50000.csv |

* MPyC 0.9 default field (64-bit prime), MPyC TLS off, t = (n-1)//2, 100 trials after 10 warm-ups, seed 20261017.
* Table I memory = peak_rss_mean_mb (mean of per-party peak RSS).

## Fabric 2.5.4 runs, every configuration and offered load

File: `tables/table2_fabric_all_runs.csv`

| config | run | MaxMessageCount | BatchTimeout | endorsement | orgs | endorsers_targeted | offered_rate_tps | concurrency | submitted | valid | invalid_or_error | window_s | tps_committed | finality_mean_s | finality_sd_s | finality_median_s | finality_p95_s | finality_p99_s | finality_min_s | finality_max_s | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bs10_bt0.2s_endorseMAJORITY_orgs2 | rate100_e2 | 10 | 0.2s | MAJORITY | 2 | 2 | 100.00 | 16 | 6000 | 6000 | 0 | 105.80 | 56.71 | 0.2818 | 0.0864 | 0.3455 | 0.3618 | 0.3674 | 0.1140 | 0.3767 | fabric/bs10_bt0.2s_endorseMAJORITY_orgs2/rate100_e2 |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | rate150_e2 | 10 | 0.2s | MAJORITY | 2 | 2 | 150.00 | 16 | 9000 | 9000 | 0 | 159.00 | 56.60 | 0.2824 | 0.0866 | 0.3462 | 0.3628 | 0.3680 | 0.1155 | 0.3937 | fabric/bs10_bt0.2s_endorseMAJORITY_orgs2/rate150_e2 |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | rate200_e2 | 10 | 0.2s | MAJORITY | 2 | 2 | 200.00 | 16 | 12000 | 12000 | 0 | 212.22 | 56.54 | 0.2828 | 0.0867 | 0.3461 | 0.3635 | 0.3693 | 0.1176 | 0.4086 | fabric/bs10_bt0.2s_endorseMAJORITY_orgs2/rate200_e2 |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | rate250_e2 | 10 | 0.2s | MAJORITY | 2 | 2 | 250.00 | 16 | 15000 | 15000 | 0 | 265.83 | 56.43 | 0.2834 | 0.0868 | 0.3469 | 0.3646 | 0.3700 | 0.1188 | 0.4135 | fabric/bs10_bt0.2s_endorseMAJORITY_orgs2/rate250_e2 |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | rate50_e2 | 10 | 0.2s | MAJORITY | 2 | 2 | 50.00 | 16 | 3000 | 3000 | 0 | 60.26 | 49.79 | 0.2061 | 0.0578 | 0.2076 | 0.2951 | 0.3062 | 0.0981 | 0.3235 | fabric/bs10_bt0.2s_endorseMAJORITY_orgs2/rate50_e2 |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | seq_e2 | 10 | 0.2s | MAJORITY | 2 | 2 | sequential | 1 | 100 | 100 | 0 | 27.98 | 3.5743 | 0.2797 | 0.0020 | 0.2789 | 0.2826 | 0.2831 | 0.2767 | 0.2838 | fabric/bs10_bt0.2s_endorseMAJORITY_orgs2/seq_e2 |
| bs10_bt2s_endorseANY_orgs2 | rate100_e1_c64 | 10 | 2s | ANY | 2 | 1 | 100.00 | 64 | 6000 | 6000 | 0 | 83.25 | 72.07 | 0.8804 | 0.2277 | 0.8837 | 1.2473 | 1.3590 | 0.1543 | 1.6259 | fabric/bs10_bt2s_endorseANY_orgs2/rate100_e1_c64 |
| bs10_bt2s_endorseANY_orgs2 | rate150_e1_c64 | 10 | 2s | ANY | 2 | 1 | 150.00 | 64 | 9000 | 9000 | 0 | 124.76 | 72.14 | 0.8841 | 0.2249 | 0.8894 | 1.2428 | 1.3734 | 0.1901 | 1.5880 | fabric/bs10_bt2s_endorseANY_orgs2/rate150_e1_c64 |
| bs10_bt2s_endorseANY_orgs2 | rate200_e1_c64 | 10 | 2s | ANY | 2 | 1 | 200.00 | 64 | 12000 | 12000 | 0 | 166.60 | 72.03 | 0.8865 | 0.2151 | 0.8971 | 1.2294 | 1.3397 | 0.2157 | 1.5381 | fabric/bs10_bt2s_endorseANY_orgs2/rate200_e1_c64 |
| bs10_bt2s_endorseANY_orgs2 | rate250_e1_c64 | 10 | 2s | ANY | 2 | 1 | 250.00 | 64 | 15000 | 15000 | 0 | 208.55 | 71.92 | 0.8884 | 0.2213 | 0.9010 | 1.2470 | 1.3611 | 0.2141 | 1.6886 | fabric/bs10_bt2s_endorseANY_orgs2/rate250_e1_c64 |
| bs10_bt2s_endorseANY_orgs2 | rate50_e1_c64 | 10 | 2s | ANY | 2 | 1 | 50.00 | 64 | 3000 | 3000 | 0 | 60.07 | 49.94 | 0.1878 | 0.0577 | 0.1888 | 0.2777 | 0.2843 | 0.0878 | 0.2916 | fabric/bs10_bt2s_endorseANY_orgs2/rate50_e1_c64 |
| bs10_bt2s_endorseANY_orgs2 | seq_e1 | 10 | 2s | ANY | 2 | 1 | sequential | 1 | 100 | 100 | 0 | 207.58 | 0.4817 | 2.0757 | 0.0024 | 2.0750 | 2.0798 | 2.0822 | 2.0712 | 2.0837 | fabric/bs10_bt2s_endorseANY_orgs2/seq_e1 |
| bs10_bt2s_endorseANY_orgs3 | rate100_e1_c64 | 10 | 2s | ANY | 3 | 1 | 100.00 | 64 | 6000 | 6000 | 0 | 84.75 | 70.80 | 0.8965 | 0.2442 | 0.8925 | 1.2885 | 1.4146 | 0.1859 | 1.6397 | fabric/bs10_bt2s_endorseANY_orgs3/rate100_e1_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate100_e2_c64 | 10 | 2s | ANY | 3 | 2 | 100.00 | 64 | 6000 | 6000 | 0 | 99.67 | 60.20 | 1.0559 | 0.2549 | 1.0617 | 1.4536 | 1.5928 | 0.2050 | 1.8850 | fabric/bs10_bt2s_endorseANY_orgs3/rate100_e2_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate100_e3_c64 | 10 | 2s | ANY | 3 | 3 | 100.00 | 64 | 6000 | 6000 | 0 | 113.80 | 52.72 | 1.2069 | 0.2831 | 1.2128 | 1.6627 | 1.7834 | 0.2588 | 2.1264 | fabric/bs10_bt2s_endorseANY_orgs3/rate100_e3_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate150_e1_c64 | 10 | 2s | ANY | 3 | 1 | 150.00 | 64 | 9000 | 9000 | 0 | 127.33 | 70.68 | 0.9024 | 0.2456 | 0.9051 | 1.2970 | 1.4323 | 0.2136 | 1.7214 | fabric/bs10_bt2s_endorseANY_orgs3/rate150_e1_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate150_e2_c64 | 10 | 2s | ANY | 3 | 2 | 150.00 | 64 | 9000 | 9000 | 0 | 149.68 | 60.13 | 1.0610 | 0.2457 | 1.0772 | 1.4470 | 1.5587 | 0.2459 | 1.8358 | fabric/bs10_bt2s_endorseANY_orgs3/rate150_e2_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate150_e3_c64 | 10 | 2s | ANY | 3 | 3 | 150.00 | 64 | 9000 | 9000 | 0 | 170.92 | 52.66 | 1.2119 | 0.2866 | 1.2215 | 1.6655 | 1.8005 | 0.3576 | 2.0991 | fabric/bs10_bt2s_endorseANY_orgs3/rate150_e3_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate200_e1_c64 | 10 | 2s | ANY | 3 | 1 | 200.00 | 64 | 12000 | 12000 | 0 | 169.74 | 70.69 | 0.9034 | 0.2336 | 0.9090 | 1.2754 | 1.4109 | 0.2378 | 1.6805 | fabric/bs10_bt2s_endorseANY_orgs3/rate200_e1_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate200_e2_c64 | 10 | 2s | ANY | 3 | 2 | 200.00 | 64 | 12000 | 12000 | 0 | 199.75 | 60.08 | 1.0632 | 0.2539 | 1.0752 | 1.4664 | 1.5910 | 0.2648 | 1.9178 | fabric/bs10_bt2s_endorseANY_orgs3/rate200_e2_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate200_e3_c64 | 10 | 2s | ANY | 3 | 3 | 200.00 | 64 | 12000 | 12000 | 0 | 228.14 | 52.60 | 1.2143 | 0.2797 | 1.2275 | 1.6595 | 1.7879 | 0.3690 | 2.0919 | fabric/bs10_bt2s_endorseANY_orgs3/rate200_e3_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate250_e1_c64 | 10 | 2s | ANY | 3 | 1 | 250.00 | 64 | 15000 | 15000 | 0 | 212.23 | 70.68 | 0.9040 | 0.2271 | 0.9094 | 1.2661 | 1.3891 | 0.2394 | 1.5959 | fabric/bs10_bt2s_endorseANY_orgs3/rate250_e1_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate250_e2_c64 | 10 | 2s | ANY | 3 | 2 | 250.00 | 64 | 15000 | 15000 | 0 | 249.89 | 60.03 | 1.0647 | 0.2703 | 1.0756 | 1.4922 | 1.6344 | 0.2821 | 1.9478 | fabric/bs10_bt2s_endorseANY_orgs3/rate250_e2_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate250_e3_c64 | 10 | 2s | ANY | 3 | 3 | 250.00 | 64 | 15000 | 15000 | 0 | 285.31 | 52.58 | 1.2155 | 0.2840 | 1.2220 | 1.6650 | 1.8003 | 0.3633 | 2.1479 | fabric/bs10_bt2s_endorseANY_orgs3/rate250_e3_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate50_e1_c64 | 10 | 2s | ANY | 3 | 1 | 50.00 | 64 | 3000 | 3000 | 0 | 60.07 | 49.94 | 0.1901 | 0.0577 | 0.1912 | 0.2797 | 0.2864 | 0.0903 | 0.2950 | fabric/bs10_bt2s_endorseANY_orgs3/rate50_e1_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate50_e2_c64 | 10 | 2s | ANY | 3 | 2 | 50.00 | 64 | 3000 | 3000 | 0 | 60.09 | 49.93 | 0.2093 | 0.0579 | 0.2106 | 0.2981 | 0.3096 | 0.1040 | 0.3213 | fabric/bs10_bt2s_endorseANY_orgs3/rate50_e2_c64 |
| bs10_bt2s_endorseANY_orgs3 | rate50_e3_c64 | 10 | 2s | ANY | 3 | 3 | 50.00 | 64 | 3000 | 3000 | 0 | 60.10 | 49.92 | 0.2423 | 0.0583 | 0.2410 | 0.3336 | 0.3447 | 0.1169 | 0.3630 | fabric/bs10_bt2s_endorseANY_orgs3/rate50_e3_c64 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate100_e2 | 10 | 2s | MAJORITY | 2 | 2 | 100.00 | 16 | 6000 | 6000 | 0 | 105.99 | 56.61 | 0.2823 | 0.0865 | 0.3461 | 0.3622 | 0.3668 | 0.1114 | 0.3756 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate100_e2 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 10 | 2s | MAJORITY | 2 | 2 | 100.00 | 64 | 6000 | 6000 | 0 | 97.49 | 61.54 | 1.0328 | 0.2398 | 1.0381 | 1.4242 | 1.5354 | 0.2124 | 1.8114 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate100_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate150_e2 | 10 | 2s | MAJORITY | 2 | 2 | 150.00 | 16 | 9000 | 9000 | 0 | 159.48 | 56.43 | 0.2833 | 0.0868 | 0.3474 | 0.3635 | 0.3694 | 0.1161 | 0.4002 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate150_e2 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate150_e2_c64 | 10 | 2s | MAJORITY | 2 | 2 | 150.00 | 64 | 9000 | 9000 | 0 | 146.37 | 61.49 | 1.0376 | 0.2362 | 1.0413 | 1.4178 | 1.5314 | 0.2181 | 1.7804 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate150_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate200_e2 | 10 | 2s | MAJORITY | 2 | 2 | 200.00 | 16 | 12000 | 12000 | 0 | 212.84 | 56.38 | 0.2836 | 0.0870 | 0.3472 | 0.3649 | 0.3702 | 0.1084 | 0.4274 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate200_e2 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate200_e2_c64 | 10 | 2s | MAJORITY | 2 | 2 | 200.00 | 64 | 12000 | 12000 | 0 | 195.82 | 61.28 | 1.0422 | 0.2374 | 1.0523 | 1.4251 | 1.5386 | 0.2884 | 1.7794 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate200_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate250_e2 | 10 | 2s | MAJORITY | 2 | 2 | 250.00 | 16 | 15000 | 15000 | 0 | 267.18 | 56.14 | 0.2849 | 0.0874 | 0.3487 | 0.3659 | 0.3708 | 0.1112 | 0.4274 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate250_e2 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate250_e2_c64 | 10 | 2s | MAJORITY | 2 | 2 | 250.00 | 64 | 15000 | 15000 | 0 | 244.57 | 61.33 | 1.0419 | 0.2285 | 1.0590 | 1.3908 | 1.5166 | 0.2753 | 1.7129 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate250_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate50_e2 | 10 | 2s | MAJORITY | 2 | 2 | 50.00 | 16 | 3000 | 3000 | 0 | 60.08 | 49.93 | 0.2050 | 0.0578 | 0.2060 | 0.2948 | 0.3039 | 0.0996 | 0.3138 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate50_e2 |
| bs10_bt2s_endorseMAJORITY_orgs2 | rate50_e2_c64 | 10 | 2s | MAJORITY | 2 | 2 | 50.00 | 64 | 3000 | 3000 | 0 | 60.08 | 49.93 | 0.2057 | 0.0579 | 0.2069 | 0.2953 | 0.3044 | 0.0986 | 0.3158 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/rate50_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs2 | seq_e2 | 10 | 2s | MAJORITY | 2 | 2 | sequential | 1 | 100 | 100 | 0 | 208.08 | 0.4806 | 2.0807 | 0.0024 | 2.0803 | 2.0840 | 2.0845 | 2.0765 | 2.0881 | fabric/bs10_bt2s_endorseMAJORITY_orgs2/seq_e2 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate100_e2_c64 | 10 | 2s | MAJORITY | 3 | 2 | 100.00 | 64 | 6000 | 6000 | 0 | 99.86 | 60.08 | 1.0579 | 0.2694 | 1.0611 | 1.4992 | 1.6486 | 0.1941 | 1.8221 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate100_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate100_e3_c64 | 10 | 2s | MAJORITY | 3 | 3 | 100.00 | 64 | 6000 | 6000 | 0 | 113.50 | 52.86 | 1.2033 | 0.2750 | 1.2123 | 1.6409 | 1.7678 | 0.2681 | 2.0525 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate100_e3_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate150_e2_c64 | 10 | 2s | MAJORITY | 3 | 2 | 150.00 | 64 | 9000 | 9000 | 0 | 149.96 | 60.02 | 1.0630 | 0.2637 | 1.0583 | 1.4886 | 1.6140 | 0.2181 | 1.8797 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate150_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate150_e3_c64 | 10 | 2s | MAJORITY | 3 | 3 | 150.00 | 64 | 9000 | 9000 | 0 | 170.68 | 52.73 | 1.2102 | 0.2795 | 1.2214 | 1.6566 | 1.7716 | 0.3240 | 2.0829 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate150_e3_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate200_e2_c64 | 10 | 2s | MAJORITY | 3 | 2 | 200.00 | 64 | 12000 | 12000 | 0 | 200.68 | 59.80 | 1.0682 | 0.2639 | 1.0771 | 1.4917 | 1.6251 | 0.3055 | 1.9544 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate200_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate200_e3_c64 | 10 | 2s | MAJORITY | 3 | 3 | 200.00 | 64 | 12000 | 12000 | 0 | 227.53 | 52.74 | 1.2111 | 0.2900 | 1.2235 | 1.6812 | 1.8220 | 0.3717 | 2.0934 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate200_e3_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate250_e2_c64 | 10 | 2s | MAJORITY | 3 | 2 | 250.00 | 64 | 15000 | 15000 | 0 | 250.78 | 59.81 | 1.0684 | 0.2648 | 1.0752 | 1.4936 | 1.6248 | 0.2833 | 1.8677 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate250_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate250_e3_c64 | 10 | 2s | MAJORITY | 3 | 3 | 250.00 | 64 | 15000 | 15000 | 0 | 284.67 | 52.69 | 1.2127 | 0.2810 | 1.2295 | 1.6539 | 1.7792 | 0.3580 | 2.1074 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate250_e3_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate50_e2_c64 | 10 | 2s | MAJORITY | 3 | 2 | 50.00 | 64 | 3000 | 3000 | 0 | 60.08 | 49.93 | 0.2103 | 0.0577 | 0.2108 | 0.3003 | 0.3091 | 0.1016 | 0.3224 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate50_e2_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | rate50_e3_c64 | 10 | 2s | MAJORITY | 3 | 3 | 50.00 | 64 | 3000 | 3000 | 0 | 60.10 | 49.91 | 0.2433 | 0.0582 | 0.2437 | 0.3328 | 0.3444 | 0.1243 | 0.3753 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/rate50_e3_c64 |
| bs10_bt2s_endorseMAJORITY_orgs3 | seq_e2 | 10 | 2s | MAJORITY | 3 | 2 | sequential | 1 | 100 | 100 | 0 | 208.15 | 0.4804 | 2.0814 | 0.0024 | 2.0818 | 2.0854 | 2.0866 | 2.0774 | 2.0873 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/seq_e2 |
| bs10_bt2s_endorseMAJORITY_orgs3 | seq_e3 | 10 | 2s | MAJORITY | 3 | 3 | sequential | 1 | 100 | 100 | 0 | 208.50 | 0.4796 | 2.0850 | 0.0024 | 2.0856 | 2.0883 | 2.0891 | 2.0812 | 2.0900 | fabric/bs10_bt2s_endorseMAJORITY_orgs3/seq_e3 |
| bs30_bt2s_endorseANY_orgs2 | rate100_e1_c64 | 30 | 2s | ANY | 2 | 1 | 100.00 | 64 | 6000 | 6000 | 0 | 82.97 | 72.32 | 0.8795 | 0.2051 | 0.8365 | 1.2857 | 1.3451 | 0.3040 | 1.4541 | fabric/bs30_bt2s_endorseANY_orgs2/rate100_e1_c64 |
| bs30_bt2s_endorseANY_orgs2 | rate150_e1_c64 | 30 | 2s | ANY | 2 | 1 | 150.00 | 64 | 9000 | 9000 | 0 | 124.59 | 72.23 | 0.8836 | 0.2032 | 0.8390 | 1.2816 | 1.3386 | 0.2699 | 1.6108 | fabric/bs30_bt2s_endorseANY_orgs2/rate150_e1_c64 |
| bs30_bt2s_endorseANY_orgs2 | rate200_e1_c64 | 30 | 2s | ANY | 2 | 1 | 200.00 | 64 | 12000 | 12000 | 0 | 166.57 | 72.04 | 0.8869 | 0.2056 | 0.8429 | 1.2921 | 1.3687 | 0.2559 | 1.6857 | fabric/bs30_bt2s_endorseANY_orgs2/rate200_e1_c64 |
| bs30_bt2s_endorseANY_orgs2 | rate250_e1_c64 | 30 | 2s | ANY | 2 | 1 | 250.00 | 64 | 15000 | 15000 | 0 | 207.93 | 72.14 | 0.8860 | 0.2045 | 0.8406 | 1.2854 | 1.3586 | 0.2694 | 1.5121 | fabric/bs30_bt2s_endorseANY_orgs2/rate250_e1_c64 |
| bs30_bt2s_endorseANY_orgs2 | rate50_e1_c64 | 30 | 2s | ANY | 2 | 1 | 50.00 | 64 | 3000 | 3000 | 0 | 60.09 | 49.93 | 0.4133 | 0.1729 | 0.4125 | 0.6822 | 0.7042 | 0.0994 | 0.7257 | fabric/bs30_bt2s_endorseANY_orgs2/rate50_e1_c64 |
| bs30_bt2s_endorseANY_orgs2 | seq_e1 | 30 | 2s | ANY | 2 | 1 | sequential | 1 | 100 | 100 | 0 | 207.58 | 0.4818 | 2.0757 | 0.0024 | 2.0752 | 2.0795 | 2.0802 | 2.0701 | 2.0826 | fabric/bs30_bt2s_endorseANY_orgs2/seq_e1 |
| bs30_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 30 | 2s | MAJORITY | 2 | 2 | 100.00 | 64 | 6000 | 6000 | 0 | 98.99 | 60.61 | 1.0504 | 0.2325 | 0.9993 | 1.5224 | 1.5913 | 0.3587 | 1.6884 | fabric/bs30_bt2s_endorseMAJORITY_orgs2/rate100_e2_c64 |
| bs30_bt2s_endorseMAJORITY_orgs2 | rate150_e2_c64 | 30 | 2s | MAJORITY | 2 | 2 | 150.00 | 64 | 9000 | 9000 | 0 | 149.07 | 60.37 | 1.0573 | 0.2267 | 1.0032 | 1.5299 | 1.6150 | 0.3540 | 1.7763 | fabric/bs30_bt2s_endorseMAJORITY_orgs2/rate150_e2_c64 |
| bs30_bt2s_endorseMAJORITY_orgs2 | rate200_e2_c64 | 30 | 2s | MAJORITY | 2 | 2 | 200.00 | 64 | 12000 | 12000 | 0 | 199.65 | 60.11 | 1.0630 | 0.2320 | 1.0070 | 1.5340 | 1.6112 | 0.3348 | 1.7619 | fabric/bs30_bt2s_endorseMAJORITY_orgs2/rate200_e2_c64 |
| bs30_bt2s_endorseMAJORITY_orgs2 | rate250_e2_c64 | 30 | 2s | MAJORITY | 2 | 2 | 250.00 | 64 | 15000 | 15000 | 0 | 249.64 | 60.09 | 1.0638 | 0.2313 | 1.0092 | 1.5344 | 1.6072 | 0.3617 | 1.7130 | fabric/bs30_bt2s_endorseMAJORITY_orgs2/rate250_e2_c64 |
| bs30_bt2s_endorseMAJORITY_orgs2 | rate50_e2 | 30 | 2s | MAJORITY | 2 | 2 | 50.00 | 16 | 3000 | 3000 | 0 | 411.43 | 7.2916 | 2.1877 | 0.0260 | 2.1891 | 2.2181 | 2.2304 | 1.7952 | 2.2533 | fabric/bs30_bt2s_endorseMAJORITY_orgs2/rate50_e2 |
| bs30_bt2s_endorseMAJORITY_orgs2 | rate50_e2_c64 | 30 | 2s | MAJORITY | 2 | 2 | 50.00 | 64 | 3000 | 3000 | 0 | 60.11 | 49.91 | 0.4443 | 0.1727 | 0.4444 | 0.7132 | 0.7394 | 0.1285 | 0.7553 | fabric/bs30_bt2s_endorseMAJORITY_orgs2/rate50_e2_c64 |
| bs30_bt2s_endorseMAJORITY_orgs2 | seq_e2 | 30 | 2s | MAJORITY | 2 | 2 | sequential | 1 | 100 | 100 | 0 | 208.03 | 0.4807 | 2.0802 | 0.0023 | 2.0796 | 2.0836 | 2.0844 | 2.0770 | 2.0852 | fabric/bs30_bt2s_endorseMAJORITY_orgs2/seq_e2 |
| bs50_bt2s_endorseANY_orgs2 | rate100_e1_c64 | 50 | 2s | ANY | 2 | 1 | 100.00 | 64 | 6000 | 6000 | 0 | 85.58 | 70.11 | 0.9077 | 0.3170 | 0.7368 | 1.4533 | 1.4927 | 0.2872 | 1.5562 | fabric/bs50_bt2s_endorseANY_orgs2/rate100_e1_c64 |
| bs50_bt2s_endorseANY_orgs2 | rate150_e1_c64 | 50 | 2s | ANY | 2 | 1 | 150.00 | 64 | 9000 | 9000 | 0 | 128.54 | 70.02 | 0.9117 | 0.3178 | 0.7403 | 1.4598 | 1.5017 | 0.4660 | 1.6237 | fabric/bs50_bt2s_endorseANY_orgs2/rate150_e1_c64 |
| bs50_bt2s_endorseANY_orgs2 | rate200_e1_c64 | 50 | 2s | ANY | 2 | 1 | 200.00 | 64 | 12000 | 12000 | 0 | 172.19 | 69.69 | 0.9168 | 0.3188 | 0.7447 | 1.4663 | 1.5093 | 0.4941 | 1.7022 | fabric/bs50_bt2s_endorseANY_orgs2/rate200_e1_c64 |
| bs50_bt2s_endorseANY_orgs2 | rate250_e1_c64 | 50 | 2s | ANY | 2 | 1 | 250.00 | 64 | 15000 | 15000 | 0 | 214.98 | 69.77 | 0.9161 | 0.3179 | 0.7445 | 1.4644 | 1.5069 | 0.4985 | 1.6022 | fabric/bs50_bt2s_endorseANY_orgs2/rate250_e1_c64 |
| bs50_bt2s_endorseANY_orgs2 | rate50_e1_c64 | 50 | 2s | ANY | 2 | 1 | 50.00 | 64 | 3000 | 3000 | 0 | 60.11 | 49.91 | 0.6417 | 0.2877 | 0.6414 | 1.0878 | 1.1331 | 0.1171 | 1.1505 | fabric/bs50_bt2s_endorseANY_orgs2/rate50_e1_c64 |
| bs50_bt2s_endorseANY_orgs2 | seq_e1 | 50 | 2s | ANY | 2 | 1 | sequential | 1 | 100 | 100 | 0 | 207.53 | 0.4819 | 2.0752 | 0.0022 | 2.0746 | 2.0788 | 2.0801 | 2.0716 | 2.0817 | fabric/bs50_bt2s_endorseANY_orgs2/seq_e1 |
| bs50_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 50 | 2s | MAJORITY | 2 | 2 | 100.00 | 64 | 6000 | 6000 | 0 | 101.76 | 58.96 | 1.0806 | 0.3727 | 0.8841 | 1.7326 | 1.7910 | 0.5235 | 2.0140 | fabric/bs50_bt2s_endorseMAJORITY_orgs2/rate100_e2_c64 |
| bs50_bt2s_endorseMAJORITY_orgs2 | rate150_e2_c64 | 50 | 2s | MAJORITY | 2 | 2 | 150.00 | 64 | 9000 | 9000 | 0 | 153.68 | 58.56 | 1.0902 | 0.3757 | 0.8930 | 1.7447 | 1.8116 | 0.4963 | 2.0292 | fabric/bs50_bt2s_endorseMAJORITY_orgs2/rate150_e2_c64 |
| bs50_bt2s_endorseMAJORITY_orgs2 | rate200_e2_c64 | 50 | 2s | MAJORITY | 2 | 2 | 200.00 | 64 | 12000 | 12000 | 0 | 205.67 | 58.35 | 1.0952 | 0.3788 | 0.8940 | 1.7505 | 1.8060 | 0.5803 | 2.0076 | fabric/bs50_bt2s_endorseMAJORITY_orgs2/rate200_e2_c64 |
| bs50_bt2s_endorseMAJORITY_orgs2 | rate250_e2_c64 | 50 | 2s | MAJORITY | 2 | 2 | 250.00 | 64 | 15000 | 15000 | 0 | 257.09 | 58.35 | 1.0956 | 0.3781 | 0.8966 | 1.7527 | 1.8127 | 0.5840 | 2.0523 | fabric/bs50_bt2s_endorseMAJORITY_orgs2/rate250_e2_c64 |
| bs50_bt2s_endorseMAJORITY_orgs2 | rate50_e2_c64 | 50 | 2s | MAJORITY | 2 | 2 | 50.00 | 64 | 3000 | 3000 | 0 | 60.15 | 49.88 | 0.7012 | 0.2879 | 0.7055 | 1.1491 | 1.1945 | 0.1650 | 1.2275 | fabric/bs50_bt2s_endorseMAJORITY_orgs2/rate50_e2_c64 |
| bs50_bt2s_endorseMAJORITY_orgs2 | seq_e2 | 50 | 2s | MAJORITY | 2 | 2 | sequential | 1 | 100 | 100 | 0 | 207.98 | 0.4808 | 2.0797 | 0.0021 | 2.0786 | 2.0831 | 2.0836 | 2.0771 | 2.0837 | fabric/bs50_bt2s_endorseMAJORITY_orgs2/seq_e2 |

* One c6i.2xlarge running the Docker test-network: 1 etcdraft orderer, one peer per org, LevelDB, TLS.
* seq = 100 sequential transactions; rateR = open loop at R tx/s for 60 s; suffix _c64 = 64 client workers, otherwise 16.
* eN = number of endorsing peers targeted by each transaction.

## Fabric summary (2 orgs, block size 10, majority unless stated)

File: `tables/table2_fabric_summary.csv`

| metric | value | config | run | submitted | valid | finality_sd_s | finality_p95_s | finality_p99_s |
|---|---|---|---|---|---|---|---|---|
| Mean finality, lone transaction, BatchTimeout 0.2 s (s) | 0.2797 | bs10_bt0.2s_endorseMAJORITY_orgs2 | seq_e2 | 100 | 100 | 0.0020 | 0.2826 | 0.2831 |
| Mean finality, lone transaction, BatchTimeout 2 s (s) | 2.0807 | bs10_bt2s_endorseMAJORITY_orgs2 | seq_e2 | 100 | 100 | 0.0024 | 2.0840 | 2.0845 |
| Mean finality at 50 tx/s offered, BatchTimeout 0.2 s (s) | 0.2061 | bs10_bt0.2s_endorseMAJORITY_orgs2 | rate50_e2 | 3000 | 3000 | 0.0578 | 0.2951 | 0.3062 |
| Committed throughput at 50 tx/s offered, BatchTimeout 0.2 s (TPS) | 49.79 | bs10_bt0.2s_endorseMAJORITY_orgs2 | rate50_e2 | 3000 | 3000 | 0.0578 | 0.2951 | 0.3062 |
| Committed throughput, 16 clients, BatchTimeout 0.2 s, max over offered loads (TPS) | 56.71 | bs10_bt0.2s_endorseMAJORITY_orgs2 | rate100_e2 | 6000 | 6000 | 0.0864 | 0.3618 | 0.3674 |
| Max committed throughput, majority, 2 orgs, 64 clients (TPS) | 61.54 | bs10_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 6000 | 6000 | 0.2398 | 1.4242 | 1.5354 |
| Max committed throughput, majority, 3 orgs, 64 clients (TPS) | 60.08 | bs10_bt2s_endorseMAJORITY_orgs3 | rate100_e2_c64 | 6000 | 6000 | 0.2694 | 1.4992 | 1.6486 |
| Max committed throughput, 1-of-n endorsement, 2 orgs, 64 clients (TPS) | 72.14 | bs10_bt2s_endorseANY_orgs2 | rate150_e1_c64 | 9000 | 9000 | 0.2249 | 1.2428 | 1.3734 |


## Figure 3 values (offered 100 tx/s for 60 s, 64 clients, BatchTimeout 2 s)

File: `tables/fig3_values.csv`

| label | config | run | tps_committed | finality_mean_s |
|---|---|---|---|---|
| Majority (baseline) | bs10_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 61.54 | 1.0328 |
| 1-of-n | bs10_bt2s_endorseANY_orgs2 | rate100_e1_c64 | 72.07 | 0.8804 |
| Block 10 | bs10_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 61.54 | 1.0328 |
| Block 30 | bs30_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 60.61 | 1.0504 |
| Block 50 | bs50_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 58.96 | 1.0806 |
| Orgs 2 | bs10_bt2s_endorseMAJORITY_orgs2 | rate100_e2_c64 | 61.54 | 1.0328 |
| Orgs 3 | bs10_bt2s_endorseMAJORITY_orgs3 | rate100_e2_c64 | 60.08 | 1.0579 |


## Pipeline, BatchTimeout 0.2 s (Table III main values)

File: `tables/table3_pipeline_bt0p2s.csv`

| config | n | t | k | trials | latency_mean_s | latency_sd_s | latency_ci95_s | latency_median_s | latency_p95_s | jobs_per_s | sharing_mean_ms | eval_mean_ms | recon_mean_ms | online_mean_ms | hash_mean_ms | commit_mean_ms | readback_verify_mean_ms | plain_numpy_mean_ms | peak_rss_party0_mb | peak_rss_max_other_parties_mb | sent_per_party_per_trial_mean_mb | oracle_match | fabric_ok | readback_verified | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 4 | 1 | 10000 | 100 | 0.3619 | 0.0024 | 0.0005 | 0.3609 | 0.3653 | 2.7631 | 29.93 | 3.0080 | 4.8540 | 7.8620 | 0.1078 | 279.74 | 44.27 | 0.1437 | 48.86 | 47.46 | 0.4006 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n4_k10000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n4_k10000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 4 | 1 | 50000 | 100 | 0.5235 | 0.0049 | 0.0010 | 0.5246 | 0.5292 | 1.9102 | 154.63 | 16.76 | 26.98 | 43.74 | 0.4751 | 280.17 | 44.48 | 0.7363 | 76.22 | 72.17 | 2.0005 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n4_k50000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n4_k50000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 4 | 1 | 100000 | 100 | 0.7239 | 0.0128 | 0.0025 | 0.7288 | 0.7371 | 1.3814 | 309.36 | 34.28 | 55.23 | 89.51 | 0.9893 | 279.82 | 44.21 | 1.2882 | 110.70 | 105.15 | 4.0005 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n4_k100000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n4_k100000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 8 | 3 | 10000 | 100 | 0.4244 | 0.0026 | 0.0005 | 0.4246 | 0.4284 | 2.3561 | 86.42 | 6.3670 | 7.5481 | 13.92 | 0.1094 | 279.71 | 44.28 | 0.3014 | 56.64 | 55.00 | 1.0016 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n8_k10000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n8_k10000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 8 | 3 | 50000 | 100 | 0.8405 | 0.0073 | 0.0014 | 0.8423 | 0.8489 | 1.1898 | 437.12 | 37.29 | 40.78 | 78.07 | 0.4714 | 280.28 | 44.56 | 1.4842 | 112.96 | 108.56 | 5.0013 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n8_k50000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n8_k50000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 8 | 3 | 100000 | 100 | 1.3573 | 0.0133 | 0.0026 | 1.3626 | 1.3707 | 0.7367 | 871.04 | 77.66 | 83.84 | 161.50 | 0.9781 | 279.49 | 44.31 | 2.4623 | 187.82 | 177.75 | 10.00 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n8_k100000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n8_k100000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 12 | 5 | 10000 | 100 | 0.4950 | 0.0029 | 0.0006 | 0.4949 | 0.4995 | 2.0203 | 151.10 | 9.4077 | 10.39 | 19.80 | 0.1107 | 279.72 | 44.25 | 0.4086 | 63.51 | 61.74 | 1.6025 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n12_k10000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n12_k10000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 12 | 5 | 50000 | 100 | 1.1870 | 0.0097 | 0.0019 | 1.1897 | 1.1993 | 0.8424 | 753.04 | 55.02 | 54.77 | 109.79 | 0.4735 | 279.39 | 44.34 | 1.8520 | 147.36 | 140.32 | 8.0021 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n12_k50000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n12_k50000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 16 | 7 | 10000 | 100 | 0.5761 | 0.0054 | 0.0011 | 0.5760 | 0.5836 | 1.7358 | 223.92 | 12.49 | 15.61 | 28.10 | 0.1104 | 279.58 | 44.40 | 0.5774 | 71.88 | 69.71 | 2.2034 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n16_k10000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n16_k10000.csv |
| bs10_bt0.2s_endorseMAJORITY_orgs2 | 16 | 7 | 50000 | 100 | 1.5763 | 0.0061 | 0.0012 | 1.5759 | 1.5856 | 0.6344 | 1104.46 | 71.39 | 75.85 | 147.24 | 0.4732 | 279.86 | 44.31 | 2.5645 | 182.17 | 173.98 | 11.00 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt0.2s_endorseMAJORITY_orgs2/n16_k50000/trials_pipeline_bs10_bt0.2s_endorseMAJORITY_orgs2_n16_k50000.csv |

* Party 0 on the Fabric node (c6i.2xlarge), parties 1..n-1 one per c6i.large node; 100 trials after 10 warm-ups.
* latency = sharing + eval + recon + hash + commit + read-back/verify; memory column for Table III = peak_rss_party0_mb.

## Pipeline, BatchTimeout 2 s (Table III values in parentheses; Table V)

File: `tables/table3_pipeline_bt2s.csv`

| config | n | t | k | trials | latency_mean_s | latency_sd_s | latency_ci95_s | latency_median_s | latency_p95_s | jobs_per_s | sharing_mean_ms | eval_mean_ms | recon_mean_ms | online_mean_ms | hash_mean_ms | commit_mean_ms | readback_verify_mean_ms | plain_numpy_mean_ms | peak_rss_party0_mb | peak_rss_max_other_parties_mb | sent_per_party_per_trial_mean_mb | oracle_match | fabric_ok | readback_verified | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bs10_bt2s_endorseMAJORITY_orgs2 | 4 | 1 | 10000 | 100 | 2.1639 | 0.0037 | 0.0007 | 2.1631 | 2.1679 | 0.4621 | 30.31 | 3.0497 | 4.9249 | 7.9746 | 0.1079 | 2080.79 | 44.71 | 0.1516 | 48.59 | 47.38 | 0.4006 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n4_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n4_k10000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 4 | 1 | 50000 | 100 | 2.3266 | 0.0028 | 0.0006 | 2.3265 | 2.3314 | 0.4298 | 155.16 | 17.48 | 27.92 | 45.40 | 0.4779 | 2080.83 | 44.76 | 0.7256 | 76.20 | 72.79 | 2.0005 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n4_k50000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n4_k50000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 4 | 1 | 100000 | 100 | 2.5289 | 0.0095 | 0.0019 | 2.5317 | 2.5394 | 0.3954 | 310.95 | 35.25 | 55.90 | 91.14 | 0.9941 | 2080.98 | 44.85 | 1.4248 | 110.71 | 104.73 | 4.0005 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n4_k100000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n4_k100000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 8 | 3 | 10000 | 100 | 2.2269 | 0.0029 | 0.0006 | 2.2264 | 2.2311 | 0.4491 | 87.04 | 6.4195 | 7.6766 | 14.10 | 0.1100 | 2080.82 | 44.81 | 0.3064 | 56.56 | 55.06 | 1.0016 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 8 | 1 | 10000 | 100 | 2.1801 | 0.0026 | 0.0005 | 2.1797 | 2.1837 | 0.4587 | 43.89 | 6.5261 | 4.9128 | 11.44 | 0.1083 | 2080.24 | 44.46 | 0.3128 | 54.01 | 52.54 | 0.8012 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000_t1/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000_t1.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 8 | 2 | 10000 | 100 | 2.2033 | 0.0025 | 0.0005 | 2.2032 | 2.2074 | 0.4539 | 65.82 | 6.4290 | 6.1466 | 12.58 | 0.1091 | 2080.31 | 44.52 | 0.3119 | 55.64 | 53.98 | 0.9014 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000_t2/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000_t2.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 8 | 3 | 10000 | 100 | 2.2257 | 0.0028 | 0.0005 | 2.2250 | 2.2302 | 0.4493 | 87.15 | 6.3951 | 7.7238 | 14.12 | 0.1108 | 2079.97 | 44.40 | 0.2947 | 56.48 | 55.13 | 1.0016 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000_t3/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000_t3.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 8 | 3 | 50000 | 100 | 2.6424 | 0.0056 | 0.0011 | 2.6428 | 2.6506 | 0.3784 | 438.44 | 37.01 | 41.31 | 78.33 | 0.4740 | 2080.37 | 44.82 | 1.4320 | 113.62 | 108.95 | 5.0013 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k50000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k50000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 8 | 3 | 100000 | 100 | 3.1593 | 0.0140 | 0.0028 | 3.1602 | 3.1780 | 0.3165 | 870.42 | 79.03 | 84.09 | 163.12 | 0.9834 | 2080.20 | 44.55 | 2.5865 | 185.82 | 176.91 | 10.00 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k100000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k100000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 12 | 5 | 10000 | 100 | 2.2962 | 0.0034 | 0.0007 | 2.2964 | 2.3018 | 0.4355 | 151.22 | 9.4912 | 10.75 | 20.25 | 0.1104 | 2080.05 | 44.61 | 0.4314 | 63.20 | 61.67 | 1.6025 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n12_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n12_k10000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 12 | 5 | 50000 | 100 | 2.9926 | 0.0116 | 0.0023 | 2.9954 | 3.0060 | 0.3342 | 756.03 | 55.90 | 55.22 | 111.12 | 0.4716 | 2080.33 | 44.68 | 2.0021 | 148.55 | 141.09 | 8.0021 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n12_k50000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n12_k50000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 16 | 7 | 10000 | 100 | 2.3785 | 0.0039 | 0.0008 | 2.3785 | 2.3843 | 0.4204 | 224.62 | 12.78 | 16.33 | 29.10 | 0.1139 | 2080.18 | 44.47 | 0.6250 | 72.13 | 69.76 | 2.2034 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n16_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n16_k10000.csv |
| bs10_bt2s_endorseMAJORITY_orgs2 | 16 | 7 | 50000 | 100 | 3.3937 | 0.0124 | 0.0025 | 3.3978 | 3.4079 | 0.2947 | 1117.44 | 72.62 | 78.63 | 151.25 | 0.4731 | 2080.03 | 44.47 | 2.4986 | 181.39 | 173.98 | 11.00 | 100/100 | 100/100 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n16_k50000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n16_k50000.csv |

* Party 0 on the Fabric node (c6i.2xlarge), parties 1..n-1 one per c6i.large node; 100 trials after 10 warm-ups.
* latency = sharing + eval + recon + hash + commit + read-back/verify; memory column for Table III = peak_rss_party0_mb.

## Component analysis, k = 10 000, BatchTimeout 2 s (Table V)

File: `tables/table5_components.csv`

| group | n | t | k | latency_mean_s | peak_rss_party0_mb | oracle_match | source |
|---|---|---|---|---|---|---|---|
| parties | 4 | 1 | 10000 | 2.1639 | 48.59 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n4_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n4_k10000.csv |
| parties | 8 | 3 | 10000 | 2.2269 | 56.56 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000.csv |
| parties | 12 | 5 | 10000 | 2.2962 | 63.20 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n12_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n12_k10000.csv |
| parties | 16 | 7 | 10000 | 2.3785 | 72.13 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n16_k10000/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n16_k10000.csv |
| threshold | 8 | 1 | 10000 | 2.1801 | 54.01 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000_t1/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000_t1.csv |
| threshold | 8 | 2 | 10000 | 2.2033 | 55.64 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000_t2/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000_t2.csv |
| threshold | 8 | 3 | 10000 | 2.2257 | 56.48 | 100/100 | pipeline/bs10_bt2s_endorseMAJORITY_orgs2/n8_k10000_t3/trials_pipeline_bs10_bt2s_endorseMAJORITY_orgs2_n8_k10000_t3.csv |

* threshold rows use pipeline_bench.py -T t with n = 8.

## Inter-node round-trip time (ICMP)

File: `tables/rtt_summary.csv`

| path | pairs | mean_of_pair_avg_ms | median_ms | min_pair_avg_ms | max_pair_avg_ms |
|---|---|---|---|---|---|
| smpc_to_smpc | 240 | 0.1510 | 0.1400 | 0.0900 | 0.3180 |
| smpc_to_fabric_node | 16 | 0.2436 | 0.2145 | 0.1880 | 0.5000 |

* Source: env/rtt_ping_fullmesh.txt; one line per ordered pair (20 pings).

## Correctness totals over all AWS runs

File: `tables/correctness_totals.csv`

| smpc_trials | smpc_oracle_match | pipeline_trials | pipeline_oracle_match | pipeline_fabric_ok | pipeline_readback_verified | fabric_transactions | fabric_valid |
|---|---|---|---|---|---|---|---|
| 800 | 800 | 2300 | 2300 | 2300 | 2300 | 588900 | 588900 |

